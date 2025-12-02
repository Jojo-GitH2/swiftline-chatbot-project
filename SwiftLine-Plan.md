# SwiftLine Chatbot Assessment - Implementation Plans

## Overview
This document outlines three approaches to architect and deploy an AI-powered chatbot for SwiftLine logistics, where customers retrieve order information by tracking number.

---

## OPTION A: AWS Lex-Based Architecture

**TL;DR:** Use managed AWS Lex service for intent recognition and slot filling. Faster to build, leverages Alexa's NLU, less custom code. Best for demonstrating AWS managed services knowledge within tight timeline.

### Implementation Steps

1. **Design Lex bot structure**
   - Define 3-5 intents (e.g., `GetOrderStatus`, `TrackDelivery`, `ContactSupport`)
   - Map required slots (trackingId, orderDate, etc.)
   - Create utterance variations for each intent

2. **Create Lex bot via AWS Console**
   - Build bot, configure intent-to-slot relationships
   - Set up confidence thresholds
   - Enable session attributes for context retention

3. **Implement Lambda fulfillment function**
   - Write function triggered by Lex intent
   - Queries DynamoDB order table
   - Validates response, returns formatted order details to Lex

4. **Set up DynamoDB orders table**
   - Create table with `trackingId` partition key
   - Populate sample order data from assessment requirements

5. **Configure Lex → Lambda integration**
   - Link fulfillment intent to Lambda function
   - Test intent matching in Lex console
   - Validate slot filling behavior

6. **Deploy API Gateway endpoint**
   - Create REST API with POST integration to Lex Runtime (PostText API)
   - Format requests/responses for chatbot interaction

7. **Add CloudWatch logging**
   - Enable conversation logs in Lex (text to CloudWatch)
   - Lambda logs
   - Structured error tracking

8. **Create Terraform for AWS resources**
   - IaC for DynamoDB, Lambda, API Gateway, IAM roles
   - Lex bot export
   - Resource tagging (`Assessment: SolutionsEngineer-[YourUsername]`)

9. **Build comprehensive documentation**
   - Architecture diagram (Lex → API Gateway → Lambda → DynamoDB flow)
   - Design document explaining intent model and slot filling logic
   - Deployment instructions
   - API usage guide

10. **Deploy, test, submit**
    - Use Terraform for deployment
    - Test 5+ tracking numbers
    - Capture CloudWatch logs
    - Prepare endpoint URL and submission package

### Key Considerations

- **Lex Intent Complexity:** Start with 1-2 intents (track order, get status) or expand to 5+ (requires more utterance training data). Simpler = faster delivery.
- **Utterance Training Data:** How many utterance variations per intent? (10 = basic, 20+ = production-grade). Time trade-off.
- **Multi-turn Conversations:** Does bot need to ask clarifying questions, or is single-turn (user provides trackingId) sufficient?
- **Slot Validation:** Implement custom validation Lambda for trackingId format (regex: `SWL-YYYY-[AIR|SEA|ROAD]-XXXXX`)?

### Metrics

| Metric | Value |
|--------|-------|
| **Time Investment** | 3-5 days |
| **Code Volume** | 300-500 lines |
| **Scalability** | Automatic (AWS managed) |
| **Cost** | ~$750/month at 1M requests |
| **Assessment Impression** | "Knows AWS services" |

---

## OPTION B: Lambda + API Gateway Architecture

**TL;DR:** Build custom chatbot using Lambda + API Gateway + simple NLU. More control, showcases full-stack engineering, demonstrates architecture design. Best for demonstrating comprehensive AWS knowledge and custom logic.

### Implementation Steps

1. **Design API architecture**
   - Create REST API structure: `POST /chat` (send message)
   - Request body: `{userId, message, trackingId}`
   - Response: `{intent, confidence, orderDetails, error}`
   - Design conversation state schema

2. **Implement intent classification Lambda**
   - Build NLU function using keyword matching + regex or OpenAI API
   - Classify messages into intents (e.g., "track order", "get details", "delivery status")
   - Low-cost API integration (if choosing external NLU)

3. **Create order lookup Lambda**
   - Function queries DynamoDB by trackingId
   - Returns formatted order details
   - Handles missing records with proper error responses

4. **Set up DynamoDB tables**
   - Create `Orders` table (trackingId partition key)
   - Optionally create `ConversationHistory` table (userId + timestamp composite key)

5. **Implement conversation state management**
   - DynamoDB handler stores/retrieves user context
   - Previous queries, session info retention
   - Enables multi-turn conversation flow

6. **Configure API Gateway**
   - Create REST API, integrate with intent classification Lambda
   - Implement request validation
   - Response formatting
   - CORS headers

7. **Add error handling & validation**
   - Comprehensive error responses (400, 404, 500)
   - Input sanitization
   - TrackingId format validation

8. **Implement CloudWatch logging**
   - Structured JSON logs at Lambda entry/exit
   - DynamoDB query logs
   - NLU confidence scores
   - Error stack traces
   - Request/response samples

9. **Write Terraform infrastructure**
   - IaC for Lambda functions (intent classifier, order lookup)
   - API Gateway
   - DynamoDB tables
   - IAM roles
   - CloudWatch Log Groups
   - Proper tagging

10. **Create documentation**
    - Architecture diagram (API Gateway → Lambda → DynamoDB flow)
    - Design doc covering API schema, intent model, state management approach
    - Error handling strategy
    - Deployment instructions

11. **Deploy, test, submit**
    - Terraform deploy
    - Test API with curl/Postman (10+ scenarios)
    - Verify CloudWatch logs and error handling
    - Prepare endpoint URL

### Key Considerations

- **NLU Approach:** Use simple keyword matching (fast, limited) vs. OpenAI API (smart, costs $0.001/request) vs. custom ML model (complex, time-intensive).
- **Conversation Complexity:** Single-turn (user provides trackingId in one message) vs. multi-turn (bot asks questions sequentially).
- **External NLU Service:** Integrate OpenAI/Anthropic, or build custom classifier?
- **API Authentication:** Public endpoint for demo, or API key/IAM auth?
- **Conversation Persistence:** Store full chat history in DynamoDB, or stateless API?

### Metrics

| Metric | Value |
|--------|-------|
| **Time Investment** | 5-7 days |
| **Code Volume** | 800-1200 lines |
| **Scalability** | Manual (you manage concurrency, throttling) |
| **Cost** | ~$5-10/month base (+ NLU service if external) |
| **Assessment Impression** | "Full-stack engineer" |

---

## OPTION C: Hybrid Approach (Recommended)

**TL;DR:** Implement Lambda + API Gateway in Week 1 (fast, working demo), integrate AWS Lex in Week 2 (showcase managed services, no re-architecture needed). Shows both depth and breadth.

### Implementation Steps

1. **Week 1 (Days 1-3): Build Lambda + API Gateway foundation**
   - Simple keyword-based intent classification
   - Order lookup
   - Basic conversation state
   - Deliverable: Working API endpoint

2. **Week 1 (Days 4-5): Test & document Lambda approach**
   - Full testing
   - CloudWatch logs
   - Error scenarios
   - API documentation
   - Architecture diagram

3. **Week 2 (Days 6-8): Integrate AWS Lex**
   - Keep Lambda function
   - Add Lex bot layer on top
   - API Gateway can route to both
   - Demonstrate managed service integration pattern

4. **Week 2 (Days 9-10): Compare and document**
   - Design doc explains both approaches
   - Trade-offs analysis
   - Why hybrid approach chosen
   - Future extensibility
   - Production readiness assessment

### Benefits

- ✅ Shows **full-stack engineering** (Week 1 foundation)
- ✅ Demonstrates **AWS managed services knowledge** (Week 2 Lex integration)
- ✅ Illustrates **architectural flexibility** (swappable NLU layers)
- ✅ Provides **two working implementations** to submit
- ✅ Risk mitigation (if one approach has issues, other is backup)

### Metrics

| Metric | Value |
|--------|-------|
| **Time Investment** | 7-9 days |
| **Code Volume** | 1000-1500 lines |
| **Scalability** | Automatic (Lex) + Manual (Lambda) |
| **Cost** | ~$760/month total |
| **Assessment Impression** | "Senior engineer" |

---

## Comparison Table

| **Metric** | **Lex Approach** | **Lambda Approach** | **Hybrid** |
|---|---|---|---|
| **Setup Time** | 3-5 days | 5-7 days | 7-9 days |
| **Code Volume** | 300-500 lines | 800-1200 lines | 1000-1500 lines |
| **Built-in NLU** | ✅ Yes | ❌ No (bring your own) | ✅ Both |
| **Customization** | Limited | Unlimited | Unlimited + managed |
| **Assessment Impression** | "Knows AWS services" | "Full-stack engineer" | "Senior engineer" |
| **Demo Quality** | High (smart bot) | Medium-High (depends on NLU) | Highest (dual approach) |
| **Risk Level** | Low | Medium | Low (redundancy) |
| **Cost/month (1M req)** | ~$750 | ~$5-10 base | ~$760 total |
| **Recommended?** | If time tight | If time available | **Best overall** |

---

## Assessment Requirements Checklist

All approaches must address:

- [ ] Architecture Diagram - Visual representation of solution
- [ ] Deployment Instructions - Step-by-step guide
- [ ] Source Code - All code files (Lambda functions, Terraform, etc.)
- [ ] Design Document - 2-3 pages covering:
  - [ ] Architectural decisions and rationale
  - [ ] Trade-offs considered
  - [ ] How solution addresses business problem
  - [ ] Potential improvements for production
- [ ] Demo Access - Endpoint URL or instructions to test
- [ ] Resource Tagging - `Assessment: SolutionsEngineer-[YourUsername]`

---

## Recommended Next Steps

1. **Confirm approach:** Choose Lex, Lambda, or Hybrid
2. **Define NLU preference:** If Lambda, decide on NLU strategy
3. **Set timeline milestones:** Break 7-day deadline into daily goals
4. **Create project structure:** Setup directories and file templates
5. **Begin implementation:** Start with chosen approach's Step 1
