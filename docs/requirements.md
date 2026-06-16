# Requirements Analysis: Garment E-Commerce & Analytics Platform

## 1. Functional Requirements

### Customer Features
- **Mandatory Account:** Register, login, and logout. (Guest checkout is disabled).
- **Profile Management:** Update name, email, password, and default delivery district.
- **Browse & Search:** Browse products with filters (category, size, color, price). Search products by keywords.
- **Variant Selection:** View product details (images, description) and select specific variants (Size, Color). System shows real-time stock availability for the selected variant.
- **Cart Management:** Add, remove, and update quantities of specific variants in the cart.
- **Checkout & Shipping:** Select delivery district (system automatically calculates and adds the delivery fee). Choose payment method (Cash on Delivery, Bank Transfer, Card).
- **Order Management:** Track order status. Cancel orders *only* if status is "Pending" or "Processing". If status is "Shipped", the cancel option changes to "Request Exchange".
- **Custom Tailoring:** View contact information/banner for custom tailoring inquiries (handled offline).

### Admin Features
- **Product Management:** CRUD operations for products and categories. Upload multiple images. Set regular price and optional sale price.
- **Variant & Inventory Management:** Manage stock at the **variant level** (e.g., Black T-Shirt, Size M). System auto-generates SKUs. Receive low-stock alerts when a *specific variant* drops below 10 units. Out-of-stock variants remain visible on the storefront with an "Out of Stock" badge.
- **Shipping Zones:** Map districts to specific delivery fees (e.g., Colombo = Rs. 300, Upcountry = Rs. 500).
- **Order Processing:** Update order statuses (Pending, Processing, Shipped, Delivered, Cancelled, Exchanged). Handle exchange requests for shipped items.
- **Customer Management:** View customer profiles and deactivate accounts.
- **Analytics Dashboards:** Access sales, revenue, and inventory metrics (Phase 9).

### System Features
- Store transactional data (orders, payments).
- Provide secure authentication and role-based access (Customer, Admin).
- Support ML modules for forecasting, recommendations, and segmentation (Phase 10).
- Generate analytics dashboards (Phase 9).

## 2. Non-Functional Requirements
- **Performance:** Handle 1000+ concurrent users with <2s response time.
- **Scalability:** Cloud deployment with horizontal scaling.
- **Security:** Password hashing (werkzeug.security), CSRF protection, SQL injection prevention (via SQLAlchemy ORM).
- **Reliability:** 99.9% uptime target.
- **Maintainability:** Modular architecture, documented APIs.
- **Usability:** Responsive design with Bootstrap 5, intuitive navigation.

## 3. Business Requirements
- Enable direct-to-consumer (B2C) retail sales channel as the primary MVP focus.
- Provide insights into customer behavior and product performance.
- Forecast demand to optimize production and reduce overstock.
- Build foundation for advanced analytics and BI.
- Provide a dedicated channel (contact info) for custom tailoring inquiries with varying production costs.

## 4. User Stories (Expanded)
- As a customer, I want to filter products by size and color so I can quickly find what fits me.
- As a customer, I want to see the exact delivery fee for my specific district before I pay, so I know the total cost.
- As a customer, I want to be able to cancel my order myself if it hasn't shipped yet, but I understand I can only request an exchange once it is marked 'Shipped'.
- As a customer, I want to track my order status so I know when it will arrive.
- As an admin, I want to receive low-stock alerts per variant so I can restock specific sizes/colors before they run out.
- As an admin, I want to view a dashboard of best-selling products so I can adjust marketing campaigns.
- As a data analyst, I want to generate monthly sales trend reports so I can advise management on production planning.

## 5. Use Cases (Detailed Flows)

### UC1: Customer Purchases Product
1. Customer browses products and selects a specific variant (Size/Color).
2. Customer adds the variant to the cart.
3. Customer proceeds to checkout (system verifies user is logged in).
4. Customer selects their delivery district (system calculates and adds the delivery fee) and chooses a payment method.
5. System validates the order, **deducts the specific variant stock**, and creates the order record with a "Pending" status.
6. Customer receives confirmation details.
7. Order status updates to “Processing” by Admin.

### UC2: Admin Updates Inventory
1. Admin logs into dashboard.
2. Admin navigates to inventory management.
3. Admin updates stock quantity for a specific **variant** (or adds new variants).
4. System saves changes and auto-generates SKUs if new.
5. Low-stock alerts are recalculated for variants < 10 units.

### UC3: System Generates Revenue Dashboard (Phase 9)
1. Analytics module queries sales data.
2. System aggregates revenue by day/week/month.
3. Dashboard displays line chart of revenue trends.
4. Admin views insights.

### UC4: Forecasting Module Predicts Sales (Phase 10)
1. System extracts historical sales data.
2. ML model (Prophet/XGBoost) trains on data.
3. Forecast generated for next month.
4. Results stored in reports module.
5. Admin views forecast dashboard.

## 6. Actors
- **Customer:** End-user buying clothes.
- **Admin:** Business staff managing store operations.
- **System:** Automated analytics/ML modules.

## 7. System Scope
- **In Scope:**
  - Online retail operations (catalog, cart, checkout).
  - Admin management (products, variant inventory, orders, shipping zones).
  - Analytics dashboards (Phase 9).
  - ML modules (forecasting, recommendations, segmentation - Phase 10).
- **Out of Scope (Future Enhancements / Phase 2):**
  - Guest checkout.
  - Product reviews and ratings.
  - Wishlist functionality.
  - Wholesale/B2B portal operations.
  - Automated logistics/courier API integration (using manual district fee mapping for MVP).
  - Multi-language support.
  - Mobile app version.
  - Loyalty program.