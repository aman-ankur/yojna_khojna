#!/usr/bin/env python3
"""
Script to upload multiple PDF files in parallel to Yojna Khojna backend.
"""
import asyncio
import aiohttp
import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any


async def upload_pdf(session: aiohttp.ClientSession, pdf_path: Path, backend_url: str) -> Dict[str, Any]:
    """
    Upload a single PDF file to the backend.
    
    Args:
        session: aiohttp client session
        pdf_path: Path to the PDF file
        backend_url: URL of the backend API
    
    Returns:
        Dict with the API response
    """
    url = f"{backend_url}/process-pdf"
    
    # Create form data with the PDF file
    form_data = aiohttp.FormData()
    form_data.add_field('pdf_file',
                        open(pdf_path, 'rb'),
                        filename=pdf_path.name,
                        content_type='application/pdf')
    
    print(f"Uploading {pdf_path.name}...")
    async with session.post(url, data=form_data) as response:
        if response.status not in (200, 202):
            error_text = await response.text()
            print(f"Error uploading {pdf_path.name}: {response.status} - {error_text}")
            return {"filename": pdf_path.name, "status": "error", "error": error_text}
        
        result = await response.json()
        print(f"Successfully processed {pdf_path.name}: {result['status']}")
        return result


async def upload_multiple_pdfs(pdf_paths: List[Path], backend_url: str, max_concurrent: int = 5) -> List[Dict[str, Any]]:
    """
    Upload multiple PDFs in parallel with a concurrency limit.
    
    Args:
        pdf_paths: List of paths to PDF files
        backend_url: URL of the backend API
        max_concurrent: Maximum number of concurrent uploads
    
    Returns:
        List of API responses for each PDF
    """
    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def upload_with_semaphore(pdf_path: Path) -> Dict[str, Any]:
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                return await upload_pdf(session, pdf_path, backend_url)
    
    # Create tasks for all PDFs
    tasks = [upload_with_semaphore(pdf_path) for pdf_path in pdf_paths]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    return results


def main():
    parser = argparse.ArgumentParser(description='Upload multiple PDFs to Yojna Khojna backend in parallel')
    parser.add_argument('pdf_dir', help='Directory containing PDF files to upload')
    parser.add_argument('--backend-url', default='http://localhost:8000', help='Backend API URL')
    parser.add_argument('--max-concurrent', type=int, default=5, help='Maximum number of concurrent uploads')
    parser.add_argument('--pattern', default='*.pdf', help='File pattern to match (default: *.pdf)')
    
    args = parser.parse_args()
    
    # Get all PDF files in the directory
    pdf_dir = Path(args.pdf_dir)
    if not pdf_dir.exists() or not pdf_dir.is_dir():
        print(f"Error: {args.pdf_dir} is not a valid directory")
        sys.exit(1)
    
    pdf_files = sorted(list(pdf_dir.glob(args.pattern)))
    if not pdf_files:
        print(f"No PDF files found in {args.pdf_dir} matching pattern {args.pattern}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files to upload")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf.name}")
    
    # Ask for confirmation
    response = input(f"\nUpload {len(pdf_files)} PDFs to {args.backend_url}? [y/N] ")
    if response.lower() not in ('y', 'yes'):
        print("Upload canceled")
        sys.exit(0)
    
    # Upload PDFs in parallel
    results = asyncio.run(upload_multiple_pdfs(
        pdf_files, 
        args.backend_url, 
        args.max_concurrent
    ))
    
    # Print summary
    success_count = sum(1 for r in results if r.get('status') in ('exists', 'processing_scheduled'))
    print(f"\nUpload Summary:")
    print(f"  Total: {len(pdf_files)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {len(pdf_files) - success_count}")
    
    if len(pdf_files) - success_count > 0:
        print("\nFailed uploads:")
        for result in results:
            if result.get('status') not in ('exists', 'processing_scheduled'):
                print(f"  {result.get('filename', 'Unknown')}: {result.get('error', 'Unknown error')}")


if __name__ == '__main__':
    main() 