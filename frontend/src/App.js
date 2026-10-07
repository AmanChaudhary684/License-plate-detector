import React, { useState, useRef } from 'react';
import { Upload, Camera, AlertCircle, CheckCircle2, Loader2, ImageIcon, Sparkles, Zap, Eye, Download, X } from 'lucide-react';

export default function LicensePlateDetector() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        setError('File size should be less than 10MB');
        return;
      }
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
      setUploadProgress(0);
    }
  };

  const handleSubmit = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('image', selectedImage);

    const progressInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 90));
    }, 200);

    try {
      const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${API_BASE}/api/detect`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.error || 'Detection failed');
      }
    } catch (err) {
      clearInterval(progressInterval);
      setError('Failed to connect to server. Make sure Flask is running on port 5000.');
    } finally {
      setLoading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const downloadImage = (base64Data, filename) => {
    const link = document.createElement('a');
    link.href = `data:image/jpeg;base64,${base64Data}`;
    link.download = filename;
    link.click();
  };

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '2rem',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    header: {
      textAlign: 'center',
      marginBottom: '3rem',
      color: 'white'
    },
    title: {
      fontSize: '3.5rem',
      fontWeight: 'bold',
      margin: '0 0 1rem 0',
      textShadow: '0 4px 6px rgba(0,0,0,0.3)'
    },
    subtitle: {
      fontSize: '1.25rem',
      opacity: 0.9,
      margin: 0
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
      gap: '2rem',
      maxWidth: '1400px',
      margin: '0 auto'
    },
    card: {
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '20px',
      padding: '2rem',
      boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
    },
    cardHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '1.5rem'
    },
    cardTitle: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      margin: 0,
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem'
    },
    uploadZone: {
      border: '3px dashed #cbd5e0',
      borderRadius: '15px',
      padding: '3rem',
      textAlign: 'center',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      background: '#f7fafc'
    },
    uploadZoneActive: {
      border: '3px dashed #667eea',
      background: '#edf2f7',
      transform: 'scale(1.02)'
    },
    preview: {
      maxHeight: '400px',
      width: '100%',
      objectFit: 'contain',
      borderRadius: '10px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
    },
    button: {
      width: '100%',
      padding: '1rem',
      fontSize: '1.1rem',
      fontWeight: 'bold',
      border: 'none',
      borderRadius: '10px',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '0.5rem',
      marginTop: '1.5rem',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
    },
    buttonDisabled: {
      background: '#cbd5e0',
      cursor: 'not-allowed',
      boxShadow: 'none'
    },
    progressBar: {
      height: '8px',
      background: '#e2e8f0',
      borderRadius: '10px',
      overflow: 'hidden',
      marginTop: '1rem'
    },
    progressFill: {
      height: '100%',
      background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
      transition: 'width 0.3s ease'
    },
    error: {
      background: 'rgba(248, 113, 113, 0.1)',
      border: '2px solid #f87171',
      borderRadius: '10px',
      padding: '1rem',
      marginTop: '1rem',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '0.75rem'
    },
    resultImage: {
      width: '100%',
      borderRadius: '10px',
      marginTop: '0.75rem',
      boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
    },
    ocrCard: {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '12px',
      padding: '1.5rem',
      color: 'white',
      marginTop: '1rem'
    },
    ocrText: {
      fontSize: '2rem',
      fontWeight: 'bold',
      margin: '0 0 0.5rem 0',
      letterSpacing: '2px'
    },
    confidence: {
      display: 'flex',
      alignItems: 'center',
      gap: '1rem'
    },
    confidenceBar: {
      flex: 1,
      height: '8px',
      background: 'rgba(255, 255, 255, 0.3)',
      borderRadius: '10px',
      overflow: 'hidden'
    },
    confidenceFill: {
      height: '100%',
      background: 'white',
      borderRadius: '10px',
      transition: 'width 0.5s ease'
    },
    stats: {
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: '1rem',
      marginTop: '1.5rem'
    },
    statCard: {
      background: '#f7fafc',
      borderRadius: '10px',
      padding: '1rem',
      textAlign: 'center'
    },
    statValue: {
      fontSize: '1.75rem',
      fontWeight: 'bold',
      color: '#667eea',
      margin: '0 0 0.25rem 0'
    },
    statLabel: {
      fontSize: '0.85rem',
      color: '#718096',
      margin: 0
    },
    features: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '1.5rem',
      maxWidth: '1400px',
      margin: '3rem auto 0'
    },
    feature: {
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '15px',
      padding: '1.5rem',
      boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
      transition: 'transform 0.3s ease'
    },
    iconButton: {
      background: 'transparent',
      border: 'none',
      cursor: 'pointer',
      padding: '0.5rem',
      borderRadius: '8px',
      transition: 'background 0.2s ease'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>
          🚗 AI License Plate Detection
        </h1>
        <p style={styles.subtitle}>
          Advanced fog removal, real-time detection, and intelligent OCR
        </p>
      </div>

      <div style={styles.grid}>
        {/* Upload Section */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <h2 style={styles.cardTitle}>
              <Upload size={24} />
              Upload Image
            </h2>
            {selectedImage && (
              <button
                style={styles.iconButton}
                onClick={handleReset}
                onMouseOver={(e) => e.currentTarget.style.background = '#f7fafc'}
                onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <X size={20} />
              </button>
            )}
          </div>

          <label style={{cursor: 'pointer'}}>
            <div
              style={previewUrl ? {...styles.uploadZone, ...styles.uploadZoneActive} : styles.uploadZone}
              onMouseOver={(e) => !previewUrl && (e.currentTarget.style.background = '#edf2f7')}
              onMouseOut={(e) => !previewUrl && (e.currentTarget.style.background = '#f7fafc')}
            >
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" style={styles.preview} />
              ) : (
                <div>
                  <ImageIcon size={64} color="#cbd5e0" style={{margin: '0 auto 1rem'}} />
                  <p style={{fontSize: '1.1rem', margin: '0 0 0.5rem 0', color: '#2d3748'}}>
                    Drop image here or click to browse
                  </p>
                  <p style={{fontSize: '0.9rem', margin: 0, color: '#718096'}}>
                    Supports JPG, PNG, JPEG • Max 10MB
                  </p>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              style={{display: 'none'}}
            />
          </label>

          {loading && uploadProgress > 0 && (
            <div style={styles.progressBar}>
              <div style={{...styles.progressFill, width: `${uploadProgress}%`}} />
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!selectedImage || loading}
            style={!selectedImage || loading ? {...styles.button, ...styles.buttonDisabled} : styles.button}
            onMouseOver={(e) => !loading && selectedImage && (e.currentTarget.style.transform = 'scale(1.05)')}
            onMouseOut={(e) => !loading && selectedImage && (e.currentTarget.style.transform = 'scale(1)')}
          >
            {loading ? (
              <>
                <Loader2 size={24} style={{animation: 'spin 1s linear infinite'}} />
                Analyzing...
              </>
            ) : (
              <>
                <Zap size={24} />
                Detect License Plate
              </>
            )}
          </button>

          {error && (
            <div style={styles.error}>
              <AlertCircle size={20} color="#f87171" />
              <span style={{color: '#991b1b', fontSize: '0.95rem'}}>{error}</span>
            </div>
          )}
        </div>

        {/* Results Section */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>
            <Eye size={24} />
            Detection Results
          </h2>

          {result ? (
            <div>
              {result.enhanced_image && (
                <div>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem'}}>
                    <strong style={{fontSize: '0.95rem', color: '#4a5568'}}>Enhanced Image</strong>
                    <button
                      style={styles.iconButton}
                      onClick={() => downloadImage(result.enhanced_image, 'enhanced.jpg')}
                      onMouseOver={(e) => e.currentTarget.style.background = '#f7fafc'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <Download size={18} />
                    </button>
                  </div>
                  <img
                    src={`data:image/jpeg;base64,${result.enhanced_image}`}
                    alt="Enhanced"
                    style={styles.resultImage}
                  />
                </div>
              )}

              {result.detected_plate && (
                <div style={{marginTop: '1.5rem'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem'}}>
                    <strong style={{fontSize: '0.95rem', color: '#4a5568'}}>Detected Plate</strong>
                    <button
                      style={styles.iconButton}
                      onClick={() => downloadImage(result.detected_plate, 'plate.jpg')}
                      onMouseOver={(e) => e.currentTarget.style.background = '#f7fafc'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <Download size={18} />
                    </button>
                  </div>
                  <img
                    src={`data:image/jpeg;base64,${result.detected_plate}`}
                    alt="Plate"
                    style={styles.resultImage}
                  />
                </div>
              )}

              {result.ocr_results && result.ocr_results.length > 0 && (
                <div>
                  {result.ocr_results.map((item, idx) => (
                    <div key={idx} style={styles.ocrCard}>
                      <div style={styles.ocrText}>{item.text}</div>
                      <div style={styles.confidence}>
                        <div style={styles.confidenceBar}>
                          <div style={{...styles.confidenceFill, width: `${item.confidence * 100}%`}} />
                        </div>
                        <span style={{fontSize: '0.9rem', fontWeight: 'bold'}}>
                          {(item.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div style={styles.stats}>
                <div style={styles.statCard}>
                  <p style={styles.statValue}>{result.processing_time?.toFixed(2)}s</p>
                  <p style={styles.statLabel}>Time</p>
                </div>
                <div style={styles.statCard}>
                  <p style={styles.statValue}>{result.plates_detected || 0}</p>
                  <p style={styles.statLabel}>Plates</p>
                </div>
                <div style={styles.statCard}>
                  <p style={styles.statValue}>{((result.detection_confidence || 0) * 100).toFixed(0)}%</p>
                  <p style={styles.statLabel}>Confidence</p>
                </div>
              </div>
            </div>
          ) : (
            <div style={{textAlign: 'center', padding: '4rem 0', color: '#cbd5e0'}}>
              <Camera size={80} style={{margin: '0 auto 1rem'}} />
              <p style={{fontSize: '1.1rem', margin: 0}}>Upload an image to see results</p>
            </div>
          )}
        </div>
      </div>

      {/* Features */}
      <div style={styles.features}>
        <div style={styles.feature}>
          <Sparkles size={32} color="#667eea" style={{marginBottom: '1rem'}} />
          <h3 style={{fontSize: '1.2rem', margin: '0 0 0.5rem 0'}}>Image Enhancement</h3>
          <p style={{color: '#718096', margin: 0, fontSize: '0.95rem'}}>
            Dark Channel Prior removes fog for crystal-clear visibility
          </p>
        </div>
        <div style={styles.feature}>
          <Zap size={32} color="#667eea" style={{marginBottom: '1rem'}} />
          <h3 style={{fontSize: '1.2rem', margin: '0 0 0.5rem 0'}}>YOLOv8 Detection</h3>
          <p style={{color: '#718096', margin: 0, fontSize: '0.95rem'}}>
            Lightning-fast deep learning for accurate plate localization
          </p>
        </div>
        <div style={styles.feature}>
          <Eye size={32} color="#667eea" style={{marginBottom: '1rem'}} />
          <h3 style={{fontSize: '1.2rem', margin: '0 0 0.5rem 0'}}>OCR Recognition</h3>
          <p style={{color: '#718096', margin: 0, fontSize: '0.95rem'}}>
            EasyOCR extracts text with high precision and confidence
          </p>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}