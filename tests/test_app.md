# App Testing

## Test 1: No Stock Selected

**Steps**
1. Launch the app.
2. Select any valid trading date.
3. Click **Analyze** without selecting any stocks.

**Expected Result**
- Warning message:
  ```
  Please select at least one stock.
  ```

---

## Test 2: Maximum Stock Limit

**Steps**
1. Launch the app.
2. Select more than 100 stocks.
3. Click **Analyze**.

**Expected Result**
- Error message:
  ```
  Please select at most 100 stocks.
  ```

---

## Test 3: One Stock Selected

**Steps**
1. Launch the app.
2. Select one stock.
3. Click **Analyze**.

**Expected Result**
- Top 20 correlated stocks table is displayed.
- Selected stock is not included in the table.
- Correlations are sorted in descending order.

---

## Test 4: Window Changes Available Dates

**Steps**
1. Select a 10-day window.
2. Note the first available trading date.
3. Change the window to 120 days.

**Expected Result**
- The first available trading date moves forward.
- Earlier dates are no longer available.

---

## Test 5: Correlation Changes with Window

**Steps**
1. Select the same stock(s) and trading date.
2. Run with a 20-day window.
3. Run again with a 60-day window.

**Expected Result**
- Correlation values differ, demonstrating that the selected window affects the calculation.

---

## Test 6: First Valid Trading Date

**Steps**
1. Select any window size.
2. Choose the earliest available trading date.
3. Select one or more stocks.
4. Click **Analyze**.

**Expected Result**
- Correlation is calculated successfully.
- No errors are displayed.
