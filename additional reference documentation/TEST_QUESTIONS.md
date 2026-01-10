# Test Questions for Multi-Agent Financial Analysis System

## 📊 Test Questions by Category

### 1. **Simple Data Queries** (FinancialAgent only)
*These should route to FinancialAgent and FINISH immediately*

1. "What is the current price of AAPL?"
2. "What was the closing price of TSLA yesterday?"
3. "Show me the latest stock data for Microsoft"
4. "What is the current stock price of GOOGL?"
5. "Get me the stock information for NVDA"

**Expected Behavior:**
- Routes to FinancialAgent
- Returns price/data
- Supervisor FINISHes immediately

---

### 2. **Visualization Requests** (FinancialAgent → CodeAgent)
*These should route to FinancialAgent first, then CodeAgent, then FINISH*

6. "Draw a plot of the closing stock prices of AAPL over the last week, with the x axis being the closing dates."
7. "Create a chart showing TSLA stock prices for the past month"
8. "Visualize the closing prices of MSFT over the last 5 days"
9. "Plot a graph of GOOGL stock prices with dates on x-axis"
10. "Show me a visualization of NVDA closing prices"

**Expected Behavior:**
- Routes to FinancialAgent (gets data)
- Routes to CodeAgent (creates plot)
- Supervisor FINISHes after CodeAgent responds
- Should NOT call CodeAgent multiple times

---

### 3. **News/Information Queries** (WebSearchAgent)
*These should route to WebSearchAgent and FINISH*

11. "What is the latest news about Apple?"
12. "Find recent information about Tesla stock performance"
13. "What are analysts saying about Microsoft's earnings?"
14. "Search for the latest news on Google's stock"
15. "What is the current market sentiment about NVIDIA?"

**Expected Behavior:**
- Routes to WebSearchAgent
- Returns comprehensive news/information
- Supervisor FINISHes after response

---

### 4. **Combined Queries** (Multiple agents)
*These may require multiple agents*

16. "What is the current price of AAPL and what's the latest news about it?"
17. "Show me TSLA stock data and find recent news articles"
18. "Get MSFT stock price and search for analyst opinions"
19. "What is GOOGL's current price and what are the latest market trends?"

**Expected Behavior:**
- Routes to FinancialAgent (for price)
- Routes to WebSearchAgent (for news)
- Supervisor FINISHes after both complete

---

### 5. **Complex Visualization Requests**
*Test edge cases and complex scenarios*

20. "Create a plot comparing AAPL and TSLA closing prices over the last week"
21. "Draw a chart showing the stock prices of MSFT, GOOGL, and NVDA for the past month"
22. "Visualize the closing prices of AAPL with proper date formatting on the x-axis"
23. "Create a graph showing TSLA stock prices with title, labels, and formatted dates"

**Expected Behavior:**
- Routes to FinancialAgent (gets data for multiple stocks)
- Routes to CodeAgent (creates comparison plot)
- Should handle multiple stocks correctly
- Should format dates properly

---

### 6. **Date-Specific Queries**
*Test date handling and formatting*

24. "What was the stock price of AAPL on December 1st?"
25. "Show me TSLA prices for the last 7 days"
26. "Get MSFT closing prices for the past week"
27. "What were the stock prices of GOOGL last month?"

**Expected Behavior:**
- Routes to FinancialAgent
- Returns data with properly formatted dates
- Supervisor FINISHes after response

---

### 7. **Comparison Queries**
*Test multi-stock comparisons*

28. "Compare the stock prices of AAPL and MSFT"
29. "Show me a comparison of TSLA and GOOGL prices"
30. "What are the differences between NVDA and AMD stock prices?"

**Expected Behavior:**
- Routes to FinancialAgent (may need multiple calls or single call)
- Returns comparison data
- Supervisor FINISHes after response

---

### 8. **Edge Cases & Error Handling**
*Test robustness and error handling*

31. "What is the price of INVALIDTICKER?" (Invalid ticker)
32. "Get stock data for XYZ123" (Non-existent ticker)
33. "What is the price of" (Incomplete query)
34. "Show me a plot of AAPL prices from 100 years ago" (Invalid date range)
35. "Draw a chart of" (Incomplete visualization request)

**Expected Behavior:**
- Should handle errors gracefully
- Should return error messages
- Should not crash or loop infinitely
- Supervisor should FINISH even on errors

---

### 9. **Multi-Step Complex Queries**
*Test complex workflows*

36. "Get the current price of AAPL, find the latest news, and create a plot of its prices over the last week"
37. "What is TSLA's price, what are analysts saying, and show me a chart of its performance"
38. "Get MSFT stock data, search for recent news, and visualize the price trends"

**Expected Behavior:**
- Routes to FinancialAgent (price)
- Routes to WebSearchAgent (news)
- Routes to FinancialAgent again (data for plot)
- Routes to CodeAgent (visualization)
- Supervisor FINISHes after all complete

---

### 10. **Follow-up Questions** (Same Thread)
*Test conversation continuity*

39. First: "What is the price of AAPL?"
   Then: "Now show me a plot of it"
   Then: "What about TSLA?"

40. First: "Get me AAPL stock data"
   Then: "Create a visualization"
   Then: "Find news about Apple"

**Expected Behavior:**
- Should maintain context across questions
- Should use same thread_id
- Should route correctly based on conversation history

---

## 🎯 Testing Checklist

### Basic Functionality
- [ ] Simple price queries work
- [ ] Visualization requests generate plots
- [ ] News queries return information
- [ ] Combined queries work correctly

### Agent Routing
- [ ] FinancialAgent routes correctly for data queries
- [ ] CodeAgent routes correctly for visualization requests
- [ ] WebSearchAgent routes correctly for news queries
- [ ] Supervisor FINISHes at appropriate times

### Loop Prevention
- [ ] No duplicate agent calls
- [ ] CodeAgent doesn't get called multiple times for same plot
- [ ] Loop detection works correctly
- [ ] MAX_ITERATIONS limit works

### Error Handling
- [ ] Invalid tickers handled gracefully
- [ ] Incomplete queries don't crash
- [ ] Error messages are clear
- [ ] System recovers from errors

### Response Quality
- [ ] Responses are concise (1-2 paragraphs)
- [ ] Data is properly formatted
- [ ] Dates are human-readable
- [ ] Visualizations have proper labels

### Performance
- [ ] Queries complete in reasonable time
- [ ] No hanging or infinite loops
- [ ] Multiple questions in same thread work
- [ ] System handles 10+ questions in one thread

---

## 📝 Recommended Testing Order

1. **Start Simple**: Test basic queries (1-5)
2. **Test Visualizations**: Test plot generation (6-10)
3. **Test News**: Test web search (11-15)
4. **Test Combined**: Test multi-agent workflows (16-19)
5. **Test Complex**: Test edge cases (20-27)
6. **Test Errors**: Test error handling (31-35)
7. **Test Continuity**: Test conversation threads (39-40)

---

## 🔍 What to Look For

### ✅ Good Signs
- Fast response times
- Correct agent routing
- Clean, concise responses
- Proper plot generation
- No duplicate calls
- Graceful error handling

### ⚠️ Warning Signs
- Multiple identical agent calls
- Very long responses (>1000 words unnecessarily)
- Missing plot labels or dates
- Hanging or timeout issues
- Infinite loops
- Poor error messages

---

## 💡 Tips for Testing

1. **Test in Notebook First**: Use the notebook for interactive testing
2. **Test in Django UI**: Verify web interface works correctly
3. **Check Metrics**: Monitor metrics dashboard for performance
4. **Test Edge Cases**: Don't just test happy paths
5. **Test Conversation Flow**: Try multiple questions in same thread
6. **Verify Loop Prevention**: Intentionally try to trigger loops
7. **Check Response Length**: Ensure responses are concise

---

## 🎓 Example Test Session

```
Question 1: "What is the price of AAPL?"
Expected: FinancialAgent → FINISH (2 agent responses)

Question 2: "Draw a plot of AAPL prices"
Expected: FinancialAgent → CodeAgent → FINISH (4 agent responses)

Question 3: "What's the latest news about Apple?"
Expected: WebSearchAgent → FINISH (2 agent responses)

Question 4: "Compare AAPL and TSLA prices"
Expected: FinancialAgent → FINISH (2 agent responses)

Question 5: "Create a chart comparing them"
Expected: FinancialAgent → CodeAgent → FINISH (4 agent responses)

Total: ~14 agent responses (well under MAX_ITERATIONS = 40)
```

---

## 📊 Success Metrics

- **Response Time**: < 30 seconds for simple queries, < 2 minutes for visualizations
- **Accuracy**: Correct data and proper routing
- **Conciseness**: Responses 1-2 paragraphs (unless complex topic)
- **Reliability**: No crashes, proper error handling
- **Loop Prevention**: No duplicate agent calls
- **User Experience**: Clear, helpful responses

