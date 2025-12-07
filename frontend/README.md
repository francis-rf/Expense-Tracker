# Expense Manager - Frontend

## 🎨 Overview

A stunning, modern expense tracking application with glassmorphism design, smooth animations, and comprehensive analytics.

## ✨ Features

### 📝 **Tab 1: Manage Expenses**

- **Add Expenses**: Beautiful form to add new expenses with categories
- **View Expenses**: Real-time list of all expenses with smooth animations
- **Filter by Date**: Quickly filter expenses for specific dates
- **Delete Expenses**: Remove expenses with confirmation
- **Categories**: 8 pre-defined categories with emoji icons
  - 🍔 Food & Dining
  - 🚗 Transport
  - 🎬 Entertainment
  - 🛍️ Shopping
  - 💡 Bills & Utilities
  - ⚕️ Healthcare
  - 📚 Education
  - 📦 Other

### 📊 **Tab 2: Analytics & Insights**

- **Date Range Selection**: Analyze expenses for any date range
- **Category Breakdown**: Visual bars showing spending by category
- **Key Insights**:
  - Total Spent in selected period
  - Top spending category
  - Daily average spending
- **Percentage Distribution**: See what percentage each category represents

### 🎯 **Header Dashboard**

- **Total Expenses**: All-time spending
- **This Month**: Current month's expenses

## 🎨 Design Features

- **Glassmorphism UI**: Modern frosted glass effect
- **Animated Background**: Floating gradient orbs
- **Smooth Transitions**: Butter-smooth animations throughout
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Dark Theme**: Easy on the eyes with vibrant accent colors
- **Interactive Elements**: Hover effects and micro-animations

## 🚀 Getting Started

### Prerequisites

- Backend server running on `http://localhost:8000`

### Running the Frontend

1. **Option 1: Simple HTTP Server (Python)**

   ```bash
   cd frontend
   python -m http.server 3000
   ```

   Open: http://localhost:3000

2. **Option 2: Live Server (VS Code Extension)**

   - Install "Live Server" extension
   - Right-click `index.html`
   - Select "Open with Live Server"

3. **Option 3: Direct File Access**
   - Simply double-click `index.html`
   - Note: May have CORS issues with API calls

## 📁 File Structure

```
frontend/
├── index.html      # Main HTML structure
├── style.css       # Glassmorphism styling & animations
├── app.js          # JavaScript logic & API integration
└── README.md       # This file
```

## 🔌 API Integration

The frontend connects to the FastAPI backend:

- `GET /` - API info
- `GET /health` - Health check
- `GET /expenses/{date}` - Fetch expenses for date
- `POST /expenses/{date}` - Add new expenses
- `DELETE /expenses/{date}` - Delete expenses for date
- `GET /summary?start_date=X&end_date=Y` - Get analytics

## 🎯 Usage Guide

### Adding an Expense

1. Fill in the form on the left
2. Select date, category, notes, and amount
3. Click "Add Expense"
4. See real-time toast notification
5. View it appear in the expense list

### Viewing Expenses

1. Expenses auto-load for today's date
2. Use the filter input to select a specific date
3. Click "Filter" to load expenses for that date
4. Click "Clear" to return to today

### Deleting Expenses

1. Click the 🗑️ Delete button on any expense
2. Confirm the deletion
3. All expenses for that date will be deleted

### Viewing Analytics

1. Switch to "Analytics & Insights" tab
2. Select start and end dates
3. Click "Analyze"
4. View beautiful category breakdown and insights

## 🎨 Color Scheme

- **Primary Gradient**: Purple to violet (#667eea → #764ba2)
- **Secondary Gradient**: Pink to red (#f093fb → #f5576c)
- **Success Gradient**: Blue to cyan (#4facfe → #00f2fe)
- **Accent Gradient**: Pink to yellow (#fa709a → #fee140)
- **Background**: Deep dark blue (#0a0e27)

## 🔧 Customization

### Changing API URL

Edit `app.js`:

```javascript
const API_BASE_URL = "http://your-api-url:port";
```

### Adding Categories

Edit `index.html` in the select dropdown:

```html
<option value="YourCategory">🎯 Your Category</option>
```

And update the icon mapping in `app.js`:

```javascript
const icons = {
  YourCategory: "🎯",
  // ... other categories
};
```

### Changing Colors

Modify CSS variables in `style.css`:

```css
:root {
  --primary-gradient: linear-gradient(
    135deg,
    #your-color 0%,
    #your-color-2 100%
  );
}
```

## 📱 Responsive Breakpoints

- **Desktop**: > 1200px (Full layout)
- **Tablet**: 768px - 1200px (Stacked cards)
- **Mobile**: < 768px (Single column)

## 🎭 Animations

- **Page Load**: Smooth slide-in animations
- **Tab Switch**: Fade transitions
- **Expense Add**: Slide-in from right
- **Category Bars**: Animated fill with shimmer effect
- **Background**: Floating gradient orbs
- **Hover Effects**: Scale and glow on interactive elements

## 🐛 Troubleshooting

### Expenses not loading

- Check backend is running on port 8000
- Check browser console for errors
- Verify CORS is enabled in backend

### Date filter not working

- Ensure date format is YYYY-MM-DD
- Check that backend has data for that date

### Analytics not showing

- Select valid date range
- Ensure end date is after start date
- Check that expenses exist in that range

## 🚀 Performance

- **Lightweight**: No heavy frameworks
- **Fast Loading**: Minimal dependencies
- **Smooth Animations**: Hardware-accelerated CSS
- **Optimized Images**: SVG icons only

## 📄 License

Part of the Expense Manager project.

## 🎉 Enjoy tracking your expenses in style!
