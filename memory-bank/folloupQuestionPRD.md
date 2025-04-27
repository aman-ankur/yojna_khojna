# Follow-up Question Suggestion Feature - PRD

## 1. Feature Overview

Implement a "Suggested Questions" feature that presents users with 3-5 relevant follow-up questions after each assistant response. This feature will help low-literacy users navigate conversations about government schemes more effectively by suggesting logical next questions based on conversation context.

## 2. User Experience

- After the chatbot provides an answer, 3-5 clickable question chips appear below the response
- Questions display as horizontal scrollable chips for easy mobile navigation
- Clicking a chip automatically submits that question to the chat
- Questions are contextually relevant to the current conversation topic and previous answer
- Language matches the current conversation (Hindi or English)
- Design follows the existing Claude-inspired UI aesthetics

## 3. Functional Requirements

### 3.1 Question Generation System

Implement a hybrid system that:

- Generates contextual questions based on the latest conversation and detected entities
- Supplements with fixed template questions when appropriate
- Prioritizes questions based on likely user intent and information gaps
- Ensures questions maintain natural conversational flow

### 3.2 Question Display Component

- Create a horizontally scrollable container for question chips
- Ensure chips have distinct visual styling to indicate they are interactive
- Implement smooth scrolling behavior for mobile users
- Support 3-5 questions of varying text length
- Ensure proper spacing and visibility on all screen sizes

### 3.3 Question Categories Logic

Generate follow-up questions targeting the following categories based on relevance:

1. **Eligibility Clarification** - Personal qualification questions
2. **Application Process** - Steps, procedures, where to apply
3. **Document Requirements** - What documents are needed, alternatives
4. **Benefits & Amounts** - Financial details, in-kind benefits
5. **Timelines & Deadlines** - Application windows, processing times
6. **Contact Information** - Who to contact, where to go for help
7. **Related Schemes** - Similar or complementary programs
8. **Personal Situation** - Questions about applying the scheme to specific situations

## 4. Question Generation Strategy

### 4.1 Core Logic

1. Analyze the most recent user query and assistant response
2. Extract key entities, topics, and information gaps
3. Determine which question categories are most relevant
4. Generate a mix of:
   - Context-specific questions based on extracted entities (60%)
   - Template-based questions from the most relevant categories (40%)
5. Rank and select the top 3-5 questions based on relevance scoring

### 4.2 Entity-Based Question Generation

- Use the existing entity extraction system to identify scheme names, monetary amounts, eligibility criteria, etc.
- For each detected entity type, apply specific question templates
- Example: If a scheme name is detected, generate questions about eligibility, benefits, and application process for that specific scheme

### 4.3 Information Gap Analysis

- Identify what information has not yet been covered in the conversation
- Generate questions targeting those gaps
- Example: If benefits were mentioned but application process wasn't, prioritize application process questions

## 5. Question Categories & Templates

### 5.1 Eligibility Templates
- "Am I eligible for [scheme] if [common situation]?"
- "What are the income limits for [scheme]?"
- "Can I apply for [scheme] if I'm from [category/location]?"

### 5.2 Application Process Templates
- "What is the step-by-step process to apply for [scheme]?"
- "Where do I need to go to apply for [scheme]?"
- "Can I apply online for [scheme]?"

### 5.3 Document Requirements Templates
- "What documents do I need to apply for [scheme]?"
- "Is [specific document] required for [scheme]?"
- "What if I don't have [document] for my [scheme] application?"

### 5.4 Benefits & Amounts Templates
- "How much financial assistance will I get from [scheme]?"
- "What are all the benefits provided under [scheme]?"
- "When will I receive the money from [scheme]?"

### 5.5 Timelines & Deadlines Templates
- "What is the last date to apply for [scheme]?"
- "How long does the [scheme] application process take?"
- "When will [scheme] benefits start after approval?"

### 5.6 Contact Information Templates
- "Who should I contact if I have problems with my [scheme] application?"
- "Where is the nearest office to apply for [scheme]?"
- "Is there a helpline number for [scheme]?"

### 5.7 Related Schemes Templates
- "Are there any other schemes similar to [scheme]?"
- "What schemes are available for [demographic/need]?"
- "Can I apply for multiple schemes together?"

### 5.8 Personal Situation Templates
- "How can [scheme] help me with [common personal situation]?"
- "What if my [circumstance] changes after applying for [scheme]?"
- "Is [scheme] suitable for someone in my situation?"

## 6. Technical Considerations

### 6.1 Integration with Existing Architecture
- Integrate with the existing RAG pipeline
- Leverage the domain-specific entity extraction system
- Store and retrieve context from the conversation history
- Ensure compatibility with the current chat UI component

### 6.2 Performance Considerations
- Generate suggestions asynchronously to avoid delaying main responses
- Implement proper error handling if suggestion generation fails
- Cache common suggestions for similar queries to improve performance

### 6.3 UI Implementation
- Create a new React component for suggestion chips
- Style according to existing Material UI theme
- Implement smooth horizontal scrolling with touch support
- Ensure accessibility compliance (keyboard navigation, screen readers)

## 7. Success Metrics & Evaluation

### 7.1 Quantitative Metrics
- Suggestion click-through rate (CTR)
- Conversation length (number of turns)
- Reduction in "dead end" conversations
- User satisfaction ratings (if implemented)

### 7.2 Qualitative Evaluation
- Review sample conversations to assess suggestion relevance
- Gather feedback from user testing on suggestion quality
- Analyze patterns in which suggestion types are most/least clicked

## 8. Implementation Phases

### Phase 1: Basic Implementation
- Implement template-based suggestions for common scheme queries
- Create UI component for displaying suggestion chips
- Integrate with basic conversation flow

### Phase 2: Enhanced Contextual Awareness
- Integrate with entity extraction system
- Implement context-aware question generation
- Add information gap analysis

### Phase 3: Refinement & Optimization
- Implement suggestion ranking algorithm
- Add tracking for suggestion effectiveness
- Optimize based on usage patterns

## 9. Examples

### Example 1: Housing Scheme Query

User: "Tell me about Abua Awaas Yojana"