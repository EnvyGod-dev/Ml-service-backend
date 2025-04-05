# 🚗 Car Price Prediction API (Django + ML)

Энэ бол Django-д суурилсан REST API бөгөөд бэлтгэгдсэн машин сургалтын загварыг ашиглан машины үнийг таамаглаж байна.
---

## 📦 Requirements

Дараахыг сангуудыг суулгана уу:
```bash
pip install -r requirements.txt

⚙️ How It Works

RandomForestRegressor нь автомашины борлуулалтын түүхэн өгөгдлийг агуулсан Data.csv-г ашиглан бэлтгэгдсэн.

Сургалтанд хамрагдсан загварыг ml_model.pkl гэж хадгална

Категорийн талбаруудын шошгоны кодлогчийг label_encoders.pkl-д хадгалсан

API нь машины дэлгэрэнгүй мэдээллийг (үйлдвэрлэгч, жил, миль гэх мэт) авч, таамагласан үнийг буцаана.

🧪 Example JSON Request
Endpoint: POST /api/predict/

Request Body:
{
  "registration_year": 2016,
  "manufacture_year": 2015,
  "maker": "TOYOTA",
  "car_name": "COROLLA",
  "fuel_type": "PETROL",
  "engine_size": 1500,
  "odometer": 55000
}
✅ JSON Response
Success Response:

{
  "predicted_price": 6345.22
}
Error Response:

{
  "error": "ValueError: y contains previously unseen labels: ['NISSAN']"
}

📁 Project Structure
.
├── car_sales/
│   ├── api/
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── ml_model.py
│   ├── settings.py
│   └── ...
├── Data.csv
├── ml_model.pkl
├── label_encoders.pkl
├── train_model.py
├── requirements.txt
└── README.md

▶️ Running the App

python train_model.py

python manage.py runserver