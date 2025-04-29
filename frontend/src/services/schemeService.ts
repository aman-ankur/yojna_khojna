/**
 * Scheme Service
 * 
 * Provides access to government scheme data and related operations
 */

import { nanoid } from 'nanoid';
import conversationService from './conversationService';

// Scheme categories
export type SchemeCategory = 
  | 'agriculture'
  | 'education'
  | 'health'
  | 'housing'
  | 'employment'
  | 'financial'
  | 'social'
  | 'rural'
  | 'women';

// Scheme interface
export interface Scheme {
  id: string;
  name: string;
  description: string;
  category: SchemeCategory;
  ministryDepartment: string;
  eligibility: string[];
  benefits: string[];
  imageUrl: string;
}

// Sample data for schemes (based on actual Indian government schemes)
const sampleSchemes: Scheme[] = [
  {
    id: '1',
    name: 'PM Kisan Samman Nidhi',
    description: 'Direct income support of ₹6,000 per year for farmer families across India, transferred directly to their bank accounts in three equal installments of ₹2,000.',
    category: 'agriculture',
    ministryDepartment: 'Ministry of Agriculture & Farmers Welfare',
    eligibility: [
      'All landholding farmer families with cultivable land',
      'Small and marginal farmers with combined landholding up to 2 hectares',
      'Family defined as husband, wife and minor children'
    ],
    benefits: [
      '₹6,000 annual financial assistance in three installments',
      'Direct benefit transfer to bank accounts',
      'Reduced dependence on moneylenders for meeting farming expenses'
    ],
    imageUrl: '/images/pmkisan.png'
  },
  {
    id: '2',
    name: 'PM-KISAN-NPS',
    description: 'Extension of PM-KISAN providing voluntary pension coverage to farmers between 18-40 years. The government will match the contribution made by farmers.',
    category: 'agriculture',
    ministryDepartment: 'Ministry of Agriculture & Farmers Welfare',
    eligibility: [
      'Farmers registered under PM-KISAN',
      'Age between 18-40 years',
      'Must contribute ₹55 to ₹200 per month'
    ],
    benefits: [
      'Assured pension of ₹3,000 per month after age 60',
      'Government matches contribution made by farmer',
      'Option to increase contribution for higher pension'
    ],
    imageUrl: '/images/pmkisan-nps.png'
  },
  {
    id: '3',
    name: 'Ayushman Bharat - PMJAY',
    description: "World's largest health insurance scheme covering over 10.74 crore poor and vulnerable families providing cashless access to health services.",
    category: 'health',
    ministryDepartment: 'Ministry of Health & Family Welfare',
    eligibility: [
      'Families identified based on deprivation categories from SECC 2011',
      'Households with no adult member between age 16-59',
      'Households with no able-bodied adult member',
      'Female-headed households with no adult male member between 16-59'
    ],
    benefits: [
      'Health coverage up to ₹5 lakh per family per year',
      'Covers secondary and tertiary care hospitalization',
      'No restriction on family size, age or gender',
      'Cashless and paperless treatment at empaneled hospitals'
    ],
    imageUrl: '/images/pmjay.png'
  },
  {
    id: '4',
    name: 'PM Awas Yojana - Gramin',
    description: 'Housing for all in rural areas by providing financial assistance for construction of pucca houses to eligible rural households.',
    category: 'housing',
    ministryDepartment: 'Ministry of Rural Development',
    eligibility: [
      'Households with inadequate housing conditions',
      'Houseless families/households living in dilapidated houses',
      'Households having single room with kutcha walls and roof',
      'Priority to SC/ST, minorities, disabled, widows'
    ],
    benefits: [
      'Financial assistance of ₹1.20 lakh in plain areas and ₹1.30 lakh in difficult areas',
      'Additional MGNREGA support for 90 days of unskilled labor wages',
      'Support for toilet construction through Swachh Bharat Mission',
      'Technical assistance and facilitation'
    ],
    imageUrl: '/images/pmay-g.png'
  },
  {
    id: '5',
    name: 'PM Awas Yojana - Urban',
    description: 'Urban component providing affordable housing for the urban poor through Credit Linked Subsidy and other means.',
    category: 'housing',
    ministryDepartment: 'Ministry of Housing and Urban Affairs',
    eligibility: [
      'Economically Weaker Section (EWS) with annual income up to ₹3 lakh',
      'Low Income Group (LIG) with annual income between ₹3-6 lakh',
      'Middle Income Group-I (MIG-I) with annual income between ₹6-12 lakh',
      'Middle Income Group-II (MIG-II) with annual income between ₹12-18 lakh'
    ],
    benefits: [
      'Interest subsidy of 6.5% for EWS/LIG for loans up to ₹6 lakh',
      'Interest subsidy of 4% for MIG-I for loans up to ₹9 lakh',
      'Interest subsidy of 3% for MIG-II for loans up to ₹12 lakh',
      'Subsidy calculated on 20-year NPV basis'
    ],
    imageUrl: '/images/pmay-u.png'
  },
  {
    id: '6',
    name: 'PM Mudra Yojana',
    description: 'Provides loans up to ₹10 lakh to small and micro enterprises and individuals to enable them to set up or expand their business activities.',
    category: 'financial',
    ministryDepartment: 'Ministry of Finance',
    eligibility: [
      'Small business owners',
      'Entrepreneurs',
      'Self-employed individuals',
      'Retailers',
      'Non-farm enterprises'
    ],
    benefits: [
      'Shishu: Loans up to ₹50,000',
      'Kishore: Loans from ₹50,001 to ₹5 lakh',
      'Tarun: Loans from ₹5,00,001 to ₹10 lakh',
      'No collateral required for loans under Shishu and Kishore categories'
    ],
    imageUrl: '/images/mudra.png'
  },
  {
    id: '7',
    name: 'PM Ujjwala Yojana',
    description: 'Provides free LPG connections to women from Below Poverty Line households to reduce health hazards associated with cooking based on fossil fuels.',
    category: 'women',
    ministryDepartment: 'Ministry of Petroleum and Natural Gas',
    eligibility: [
      'Women belonging to Below Poverty Line (BPL) households',
      'SC/ST households',
      'Pradhan Mantri Awas Yojana (PMAY-G) beneficiaries',
      'Most Backward Classes',
      'Tea garden and forest dwellers',
      'Islands and river islands'
    ],
    benefits: [
      'Free LPG connection with security deposit',
      'First refill and stove free of cost',
      'Option to pay EMIs for the cost of stove and refill',
      'Special education and awareness programs'
    ],
    imageUrl: '/images/ujjwala.png'
  },
  {
    id: '8',
    name: 'PM Kaushal Vikas Yojana',
    description: 'Flagship skill development scheme aimed at enabling Indian youth to take up industry-relevant training and improve their employability.',
    category: 'employment',
    ministryDepartment: 'Ministry of Skill Development and Entrepreneurship',
    eligibility: [
      'Indian citizens who have completed 10th standard or ITI or school dropouts',
      'Age between 15-45 years (varies for different sectors)',
      'Verified Aadhaar or valid ID and bank account'
    ],
    benefits: [
      'Free skill training across 300+ job roles',
      'Stipend for travel and accommodation',
      'Certification after training completion',
      'Placement assistance in relevant industries',
      'Post-placement support'
    ],
    imageUrl: '/images/pmkvy.png'
  },
  {
    id: '9',
    name: 'Beti Bachao Beti Padhao',
    description: 'Nationwide campaign to generate awareness and improve the efficiency of welfare services for girls in India.',
    category: 'women',
    ministryDepartment: 'Ministry of Women and Child Development',
    eligibility: [
      'All girl children and their families',
      'Special focus on districts with low Child Sex Ratio',
      'All communities and regions of India'
    ],
    benefits: [
      'Scholastic benefits for girl children',
      'Awareness campaigns on gender equality',
      "Special incentives for girls' education",
      'Training programs for mothers',
      'Prevention of gender-biased sex selection'
    ],
    imageUrl: '/images/bbbp.png'
  },
  {
    id: '10',
    name: 'National Education Policy 2020',
    description: "Comprehensive education policy framework to transform India's education system with focus on equity, quality, accessibility and accountability.",
    category: 'education',
    ministryDepartment: 'Ministry of Education',
    eligibility: [
      'All students across India',
      'Educational institutions',
      'Teachers and educational professionals'
    ],
    benefits: [
      'Universal Access at all levels of education',
      'Early Childhood Care Education with new curricular structure',
      'Multiple entry/exit options in higher education',
      'Credit-based system for academic flexibility',
      'National Research Foundation for research promotion'
    ],
    imageUrl: '/images/nep2020.png'
  }
];

// Get all schemes
export const getSchemes = (): Promise<Scheme[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(sampleSchemes);
    }, 500); // Simulate network delay
  });
};

// Get all unique categories
export const getCategories = (): Promise<SchemeCategory[]> => {
  return new Promise((resolve) => {
    const categories = [...new Set(sampleSchemes.map(scheme => scheme.category))];
    setTimeout(() => {
      resolve(categories as SchemeCategory[]);
    }, 300);
  });
};

// Get schemes by category
export const getSchemesByCategory = (category: SchemeCategory): Promise<Scheme[]> => {
  return new Promise((resolve) => {
    const filteredSchemes = sampleSchemes.filter(scheme => scheme.category === category);
    setTimeout(() => {
      resolve(filteredSchemes);
    }, 300);
  });
};

// Search schemes by name or description
export const searchSchemes = (query: string): Promise<Scheme[]> => {
  return new Promise((resolve) => {
    const filteredSchemes = sampleSchemes.filter(scheme => 
      scheme.name.toLowerCase().includes(query.toLowerCase()) || 
      scheme.description.toLowerCase().includes(query.toLowerCase())
    );
    setTimeout(() => {
      resolve(filteredSchemes);
    }, 300);
  });
};

// Get all available schemes (synchronous version)
export const getAllSchemes = (): Scheme[] => {
  return sampleSchemes;
};

// Get a scheme by ID
export const getSchemeById = (id: string): Scheme | undefined => {
  return sampleSchemes.find(scheme => scheme.id === id);
};

// Get all available categories (synchronous version)
export const getAllCategories = (): SchemeCategory[] => {
  const categories = new Set<SchemeCategory>();
  sampleSchemes.forEach(scheme => categories.add(scheme.category));
  return Array.from(categories);
};

// Category color mapping - updated with more muted, professional colors
const categoryColors: Record<SchemeCategory, string> = {
  'agriculture': '#7A8C6E', // Muted sage green
  'education': '#5D6E8C', // Muted slate blue
  'employment': '#6E5D8C', // Muted dusty purple
  'financial': '#6E7A5D', // Muted olive
  'health': '#5D8C7A', // Muted teal
  'housing': '#5D7A8C', // Muted blue-gray
  'rural': '#6E8C5D', // Muted moss green
  'social': '#5D5D8C', // Muted indigo
  'women': '#8C5D7A'  // Muted mauve
};

// Get color for a category
export const getCategoryColor = (category: SchemeCategory): string => {
  return categoryColors[category] || '#617D8A'; // Default color
};

// Helper function to create a conversation about a scheme
export const createSchemeConversation = (scheme: Scheme) => {
  const newConversation = conversationService.create();
  conversationService.addMessage(newConversation.id, {
    role: 'user',
    content: `Tell me about ${scheme.name}`
  });
  return newConversation;
};

// Helper function to get a list of all categories
export const getSchemeCategories = (): SchemeCategory[] => {
  const categories = Array.from(new Set(sampleSchemes.map(scheme => scheme.category)));
  return categories as SchemeCategory[];
};

// Helper function to fetch all schemes (mocked)
export const fetchSchemes = (): Promise<Scheme[]> => {
  return new Promise((resolve) => {
    // Simulate network delay
    setTimeout(() => {
      resolve(sampleSchemes);
    }, 500);
  });
};

export default {
  getSchemes,
  getCategories,
  getAllSchemes,
  getSchemesByCategory,
  getSchemeById,
  getAllCategories,
  getCategoryColor,
  createSchemeConversation,
  getSchemeCategories,
  fetchSchemes,
  searchSchemes
}; 