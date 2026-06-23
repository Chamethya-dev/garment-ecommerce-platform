# MANSA - Garment E-Commerce & Analytics Platform

A data-driven, premium e-commerce platform tailored for a garment manufacturing business in Sri Lanka. MANSA combines a seamless shopping experience with robust inventory management and a foundation for advanced data science analytics.

##  Key Features

### 👗 Customer Experience
- **Variant-Level Shopping:** Browse garments and filter by specific variants (Size, Color) with real-time stock availability.
- **Wishlist:** Save favorite products for later.
- **Smart Checkout:** District-based delivery fee calculation (optimized for Sri Lankan geography).
- **WhatsApp Auto-Redirect:** Seamless order confirmation via WhatsApp with pre-filled order details and bank deposit instructions.
- **Flexible Payments:** Supports Cash on Delivery (COD) and Bank Deposit/Transfer.
- **Order Management:** Real-time order tracking and self-service cancellation for pending orders (with automatic stock restoration).

### ️ Admin & Operations
- **Variant Inventory Management:** Granular stock control at the Size/Color level with auto-generated SKUs and low-stock alerts.
- **Shipping Zones:** Configurable delivery fees mapped to specific districts (e.g., Matara, Colombo, Upcountry).
- **Order Processing:** Dashboard to update order statuses (Pending, Awaiting Payment, Processing, Shipped, Delivered, Cancelled).

### 📊 Data Science & Analytics (Future Phases)
- **Analytics Dashboard:** Business intelligence on revenue, sales trends, and top-selling variants.
- **Sales Forecasting:** ML models (Prophet/XGBoost) to predict future garment demand.
- **Customer Segmentation:** RFM (Recency, Frequency, Monetary) analysis for targeted marketing.

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate
- **Database:** MySQL
- **Data Science:** Pandas, Matplotlib, Scikit-Learn, Prophet
- **Deployment:** Render / Railway (Planned)

## 📁 Project Structure

```text
garment-ecommerce-platform/
├── app/                    # Main application package
│   ├── admin/              # Admin dashboard routes
│   ├── auth/               # Authentication routes
│   ├── cart/               # Cart and checkout routes
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, images, logo
│   ├── models.py           # Database models (SQLAlchemy)
│   └── routes.py           # Main customer-facing routes
├── docs/                   # Project documentation
│   ├── database_design.md
│   ├── requirements.md
│   └── use_cases.md
├── config.py               # Application configuration
├── run.py                  # Application entry point
└── README.md