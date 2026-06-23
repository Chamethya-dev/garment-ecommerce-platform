# Database Design & ER Diagram Specifications

## Overview
This database is designed to support a garment e-commerce platform with **variant-level inventory tracking**, district-based shipping, and a foundation for future data science analytics. It is normalized to 3NF.

---

## Core Entities & Tables

### 1. `users`
Stores customer and admin account information.
- `user_id` (INT, Primary Key, Auto Increment)
- `name` (VARCHAR(100), Not Null)
- `email` (VARCHAR(100), Unique, Not Null)
- `password_hash` (VARCHAR(255), Not Null)
- `phone` (VARCHAR(20), Not Null)
- `default_district` (VARCHAR(50), Null) *(Pre-fills checkout)*
- `role` (ENUM: 'customer', 'admin', Default: 'customer')
- `created_at` (TIMESTAMP, Default: Current Timestamp)

### 2. `categories`
Groups products logically (e.g., T-Shirts, Dresses).
- `category_id` (INT, Primary Key, Auto Increment)
- `name` (VARCHAR(50), Not Null)
- `slug` (VARCHAR(50), Unique, Not Null) *(For clean URLs)*

### 3. `products`
Base product information. Does NOT contain size/color/stock (handled in variants).
- `product_id` (INT, Primary Key, Auto Increment)
- `category_id` (INT, Foreign Key -> categories.category_id)
- `name` (VARCHAR(150), Not Null)
- `description` (TEXT, Null)
- `regular_price` (DECIMAL(10, 2), Not Null)
- `sale_price` (DECIMAL(10, 2), Null) *(If Null, regular_price is used)*
- `created_at` (TIMESTAMP, Default: Current Timestamp)

### 4. `product_variants` *(CRITICAL FOR GARMENTS)*
Tracks stock and attributes at the specific Size/Color level.
- `variant_id` (INT, Primary Key, Auto Increment)
- `product_id` (INT, Foreign Key -> products.product_id)
- `sku` (VARCHAR(50), Unique, Not Null) *(Auto-generated: e.g., TSH-101-BLK-M)*
- `size` (VARCHAR(10), Not Null) *(e.g., S, M, L, XL)*
- `color` (VARCHAR(50), Not Null) *(e.g., Black, White)*
- `stock_quantity` (INT, Not Null, Default: 0)

### 5. `product_images`
Allows multiple images per product.
- `image_id` (INT, Primary Key, Auto Increment)
- `product_id` (INT, Foreign Key -> products.product_id)
- `image_url` (VARCHAR(255), Not Null)
- `is_primary` (BOOLEAN, Default: False) *(True = main thumbnail in catalog)*

### 6. `shipping_zones`
Maps districts to delivery fees.
- `zone_id` (INT, Primary Key, Auto Increment)
- `zone_name` (VARCHAR(50), Not Null) *(e.g., "Colombo", "Upcountry")*
- `delivery_fee` (DECIMAL(10, 2), Not Null)
- `districts` (JSON or VARCHAR) *(Comma-separated list of districts in this zone)*

### 7. `orders`
The main order record.
- `order_id` (INT, Primary Key, Auto Increment)
- `user_id` (INT, Foreign Key -> users.user_id)
- `order_date` (TIMESTAMP, Default: Current Timestamp)
- `status` (ENUM: 'Pending', 'Awaiting Payment', 'Processing', 'Shipped', 'Delivered', 'Cancelled', Default: 'Pending')
- `subtotal` (DECIMAL(10, 2), Not Null) *(Sum of item prices)*
- `delivery_fee` (DECIMAL(10, 2), Not Null)
- `total_amount` (DECIMAL(10, 2), Not Null) *(subtotal + delivery_fee)*
- `shipping_district` (VARCHAR(50), Not Null)
- `shipping_address` (TEXT, Not Null)
- `payment_method` (VARCHAR(50), Default: 'Cash on Delivery') *(e.g., COD, Bank Deposit)*
- `notes` (TEXT, Null) *(Used for cancellation reasons or admin notes)*

### 8. `order_items`
Line items for each order. Captures the price *at the time of purchase* to protect against future price changes.
- `order_item_id` (INT, Primary Key, Auto Increment)
- `order_id` (INT, Foreign Key -> orders.order_id)
- `variant_id` (INT, Foreign Key -> product_variants.variant_id)
- `quantity` (INT, Not Null)
- `unit_price` (DECIMAL(10, 2), Not Null) *(Price of the variant at checkout)*

### 9. `wishlist`
Allows logged-in customers to save products for later.
- `wishlist_id` (INT, Primary Key, Auto Increment)
- `user_id` (INT, Foreign Key -> users.user_id)
- `product_id` (INT, Foreign Key -> products.product_id)
- `added_date` (TIMESTAMP, Default: Current Timestamp)
- *(Unique Constraint on user_id + product_id to prevent duplicates)*

---

## Key Relationships (ERD Logic)
1. **One-to-Many:** One `Category` has many `Products`.
2. **One-to-Many:** One `Product` has many `Product_Variants` and many `Product_Images`.
3. **One-to-Many:** One `User` has many `Orders` and many `Wishlist` items.
4. **One-to-Many:** One `Order` has many `Order_Items`.
5. **Many-to-One:** Many `Order_Items` can reference the same `Product_Variant`.

---

## Database Indexes (For Performance)
To ensure <2s response times and efficient querying, the following indexes will be created:
- `users.email` (Fast login lookups)
- `products.category_id` (Fast category filtering)
- `product_variants.product_id` (Fast variant fetching when viewing a product)
- `product_variants.sku` (Fast inventory lookup)
- `orders.user_id` (Fast "My Orders" page loading)
- `orders.status` (Fast Admin order filtering)

---

## Notes for Data Science (Phase 9 & 10)
- The separation of `orders` and `order_items` allows for easy aggregation of sales data (e.g., `SUM(quantity * unit_price)`).
- `product_variants` allows for granular forecasting (e.g., predicting demand specifically for "Black T-Shirt, Size M" rather than just "T-Shirt").
- `orders.status` and `orders.payment_method` provide the necessary data for RFM (Recency, Frequency, Monetary) customer segmentation and payment preference analysis.