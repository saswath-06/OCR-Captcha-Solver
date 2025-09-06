# OCR Captcha Solver 🔍

Transform CAPTCHA images into readable text with AI-powered OCR recognition. Built with deep learning and modern web technologies.

**Live Demo**: [https://ocr-captcha-solver.vercel.app](https://ocr-captcha-solver.vercel.app)

![OCR Captcha Solver Demo](https://via.placeholder.com/800x400/0f172a/22c55e?text=OCR+Captcha+Solver+Demo)

## ✨ Features

- 🤖 **AI-Powered Recognition**: Deep learning model trained on 1000+ CAPTCHA samples
- ⚡ **Real-time Processing**: Get results in under 100ms on average
- 🎨 **Modern UI**: Clean, responsive interface with drag-and-drop support
- 🔒 **Secure Processing**: Images processed in memory, not stored
- 📱 **Mobile Friendly**: Works seamlessly on all devices
- 🚀 **Production Ready**: Deployed on Railway (API) and Vercel (Frontend)

## 🏗️ Architecture

```
ocr-captcha-solver/
├── captcha-solver/          # Machine Learning Training & Models
│   ├── training.py         # Model training pipeline
│   ├── model.py           # CNN+LSTM architecture
│   ├── interferenceModel.py # ONNX inference wrapper
│   ├── configurations.py  # Model configuration
│   ├── Datasets/samples/  # Training data (1000+ images)
│   └── Results/           # Trained models & checkpoints
├── api/                   # FastAPI Backend
│   ├── main.py           # REST API endpoints
│   ├── config.py         # Model path resolution
│   └── requirements.txt  # Python dependencies
└── frontend/             # Next.js Frontend
    ├── pages/index.tsx   # Main React component
    ├── styles/globals.css # Modern dark theme
    └── package.json      # Node.js dependencies
```

## 🧠 Tech Stack

### Machine Learning
- **TensorFlow/Keras**: Deep learning framework
- **ONNX Runtime**: Optimized inference engine
- **OpenCV**: Image processing and augmentation
- **MLTU**: Custom training utilities

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **CORS**: Cross-origin resource sharing

### Frontend
- **Next.js 14**: React framework with SSR
- **TypeScript**: Type-safe JavaScript
- **CSS Variables**: Modern styling system
- **File API**: Drag-and-drop file handling

### Deployment
- **Railway**: Backend API hosting
- **Vercel**: Frontend hosting with CDN
- **GitHub**: Version control and CI/CD

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/saswath-06/OCR-Captcha-Solver.git
   cd OCR-Captcha-Solver
   ```

2. **Set up the backend**
   ```bash
   cd api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Start the API server
   uvicorn main:app --reload --port 8000
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   
   # Start the development server
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

#### Backend (Railway)
```bash
MODEL_RUN_PATH=captcha-solver/Results/202509041853
PORT=8000
```

#### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_BASE=https://ocr-detection.up.railway.app
```

### Model Configuration
The model is configured in `captcha-solver/configurations.py`:
- **Image Size**: 200×50 pixels
- **Batch Size**: 16
- **Learning Rate**: 1e-3
- **Epochs**: 1000 (with early stopping)
- **Vocabulary**: Auto-generated from dataset

## 📖 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```
Returns API status and model readiness.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_run_path": "/app/captcha-solver/Results/202509041853"
}
```

#### Predict CAPTCHA
```http
POST /api/predict
Content-Type: multipart/form-data
```

**Request:**
- `file`: Image file (PNG/JPG, max 2MB)

**Response:**
```json
{
  "text": "7dgc2",
  "timing_ms": 34
}
```

**Error Responses:**
- `400`: Invalid image
- `415`: Unsupported media type
- `503`: Model not ready
- `500`: Inference failed

## 🧪 Model Training

### Training Process
1. **Data Preparation**: Load images from `Datasets/samples/`
2. **Preprocessing**: Resize to 200×50, normalize pixel values
3. **Augmentation**: Random brightness, rotation, erosion/dilation
4. **Architecture**: CNN + Bidirectional LSTM with CTC loss
5. **Export**: Convert to ONNX for production inference

### Training Command
```bash
cd captcha-solver
python training.py
```

### Model Architecture
- **CNN Backbone**: Residual blocks with skip connections
- **Sequence Modeling**: Bidirectional LSTM (128 units)
- **Output**: CTC decoder for variable-length text
- **Loss Function**: Connectionist Temporal Classification

## 🚢 Deployment

### Railway (Backend)
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Vercel (Frontend)
1. Import GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Manual Deployment
```bash
# Backend
cd api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT

# Frontend
cd frontend
npm install
npm run build
npm start
```

## 📊 Performance

- **Inference Time**: ~30-100ms per image
- **Accuracy**: 85%+ on test dataset
- **Model Size**: ~2MB (ONNX format)
- **Memory Usage**: ~50MB (inference only)
- **Concurrent Requests**: 10+ per second

## 🔍 How It Works

1. **Image Upload**: User selects or drags CAPTCHA image
2. **Validation**: Check file type and size
3. **Preprocessing**: Resize to model input dimensions
4. **Inference**: Run through trained CNN+LSTM model
5. **Decoding**: Use CTC decoder to extract text
6. **Response**: Return predicted text with timing

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `npm test` (frontend) and `pytest` (backend)
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **TensorFlow/Keras** for the deep learning framework
- **FastAPI** for the excellent Python web framework
- **Next.js** for the React framework
- **Railway** for backend hosting
- **Vercel** for frontend hosting
- **MLTU** for training utilities

## 📞 Support

- 📧 **Email**: [your-email@example.com](mailto:your-email@example.com)
- 💬 **Discord**: [Join our community](https://discord.gg/your-server)
- 🐛 **Issues**: [GitHub Issues](https://github.com/saswath-06/OCR-Captcha-Solver/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/saswath-06/OCR-Captcha-Solver/wiki)

---

**Website** • **Documentation** • **Discord** • **Twitter**

Made with ❤️ by the OCR Captcha Solver team

# Force rebuild Sat Sep 06 17:25:00 EDT 2025
