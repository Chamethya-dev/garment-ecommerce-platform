# Use Case Specifications: Garment E-Commerce Platform

## Actors
- **Customer:** End-user browsing and purchasing garments.
- **Admin:** Business staff managing products, inventory, orders, and shipping zones.
- **System:** Automated backend processes (stock deduction, SKU generation, analytics, WhatsApp redirection).

---

## UC1: Customer Purchases a Product
**Description:** A logged-in customer selects a specific garment variant, adds it to the cart, and completes checkout with district-based shipping and WhatsApp confirmation.
**Preconditions:** Customer is registered and logged in. Product variant is in stock.
**Main Flow:**
1. Customer browses the catalog and filters by category, size, or color.
2. Customer selects a product and chooses a specific **variant** (Size and Color). System displays real-time stock availability.
3. Customer adds the variant to the shopping cart.
4. Customer proceeds to checkout. System verifies the user is logged in.
5. Customer selects their delivery district from a dropdown. System automatically calculates and adds the corresponding delivery fee to the total.
6. Customer selects a payment method (Cash on Delivery or Bank Deposit) and clicks "Place Order".
7. **System Action:** Validates the order, **deducts the stock quantity for that specific variant**, and creates the order record with a "Pending" (or "Awaiting Payment") status. Auto-generates an Order ID.
8. **System Action:** Generates a pre-formatted WhatsApp message containing the Order ID, customer details, items, and total.
9. **System Action:** Automatically redirects the customer to WhatsApp after a 3-second loading screen.
10. Customer sends the message to the business to finalize the order.
**Postconditions:** Order is created in the database, variant stock is reduced, and the customer is directed to WhatsApp to confirm.

---

## UC2: Admin Manages Variant Inventory
**Description:** Admin updates stock levels for specific garment variants, triggering automatic alerts if stock is low.
**Preconditions:** Admin is logged into the dashboard.
**Main Flow:**
1. Admin navigates to the Inventory Management section.
2. Admin selects a product to view its variants (e.g., Black T-Shirt, Size M).
3. Admin updates the `stock_quantity` for a specific variant or adds a new variant (Size/Color combination).
4. **System Action:** Saves the changes to the database. If a new variant is added, the system **auto-generates a unique SKU** (e.g., `TSH-101-BLK-M`).
5. **System Action:** Recalculates low-stock alerts. If any variant's `stock_quantity` drops below 10, it is flagged on the Admin Dashboard.
**Postconditions:** Database reflects accurate variant-level stock. Low-stock alerts are updated.

---

## UC3: Customer Cancels an Order
**Description:** A customer attempts to cancel an order based on the order's current status.
**Preconditions:** Customer is logged in and has an existing order.
**Main Flow:**
1. Customer navigates to "My Orders" and selects a specific order to track.
2. **System Action:** Checks the current `status` of the order.
   - **If status is "Pending" or "Awaiting Payment":** System displays a "Cancel Order" button. 
   - **If status is "Processing", "Shipped", or "Delivered":** System hides the cancel button and displays an informational message that the order cannot be cancelled.
3. Customer clicks "Cancel Order" (if available) and optionally provides a reason.
4. **System Action:** Updates the order status to "Cancelled", saves the reason in the `notes` column, and **automatically restores the variant stock quantities** to the inventory.
**Postconditions:** Order status is updated to "Cancelled", and inventory is accurately restored.

---

## UC4: Admin Manages Shipping Zones
**Description:** Admin configures delivery fees based on geographic districts in Sri Lanka.
**Preconditions:** Admin is logged into the dashboard.
**Main Flow:**
1. Admin navigates to Shipping Settings.
2. Admin creates or edits a Shipping Zone (e.g., "Colombo", "Upcountry", "Rest of Island").
3. Admin assigns specific districts to the zone and sets the `delivery_fee` (e.g., Colombo = Rs. 300).
4. System saves the configuration.
**Postconditions:** Checkout page dynamically calculates the correct delivery fee based on the customer's selected district.

---

## UC5: System Generates Revenue Dashboard (Phase 9)
**Description:** The system aggregates sales data to provide business insights to the Admin.
**Preconditions:** Historical order data exists in the database.
**Main Flow:**
1. Admin navigates to the Analytics Dashboard.
2. **System Action:** Queries the `orders` and `order_items` tables, filtering by date range.
3. **System Action:** Aggregates total revenue, number of orders, and top-selling variants.
4. System renders visual charts (line charts for revenue trends, bar charts for top products).
**Postconditions:** Admin views actionable business intelligence.

---

## UC6: Forecasting Module Predicts Sales (Phase 10)
**Description:** The system uses Machine Learning to predict future garment demand.
**Preconditions:** Sufficient historical sales data (minimum 6-12 months) is available.
**Main Flow:**
1. **System Action:** Extracts historical daily/weekly sales data from the database.
2. **System Action:** Trains an ML model (e.g., Prophet or XGBoost) on the historical data.
3. **System Action:** Generates a sales forecast for the upcoming month, broken down by product category or top variants.
4. System stores the forecast results in the reports module.
5. Admin views the forecast dashboard to advise production planning.
**Postconditions:** Predictive insights are available for inventory optimization.