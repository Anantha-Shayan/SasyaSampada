import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SoilCardUpload = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setExtractedData(null);
    }
  };

  const processSoilCard = async () => {
    if (!selectedFile) return;
    
    setIsProcessing(true);
    
    // Simulate OCR processing
    setTimeout(() => {
      const mockExtractedData = {
        N: 85,
        P: 45,
        K: 38,
        ph: 6.8,
        organicMatter: 2.1,
        moisture: 65,
        temperature: 24
      };
      
      setExtractedData(mockExtractedData);
      setIsProcessing(false);
    }, 3000);
  };

  const useExtractedData = () => {
    if (extractedData) {
      navigate('/advisory', { 
        state: { 
          soilData: extractedData,
          fromSoilCard: true 
        } 
      });
    }
  };

  return (
    <div className="flex h-full min-h-screen w-full flex-col justify-between">
      <div className="flex-grow">
        <header className="flex items-center justify-between p-4">
          <button 
            className="flex h-12 w-12 items-center justify-center text-gray-900 dark:text-white"
            onClick={() => navigate('/advisory')}
          >
            <span className="material-symbols-outlined text-3xl">arrow_back</span>
          </button>
          <h1 className="flex-1 text-center text-lg font-bold text-gray-900 dark:text-white pr-12">
            Upload Soil Card
          </h1>
        </header>

        <main className="p-4 space-y-6">
          {/* Upload Section */}
          <div className="flex flex-col items-center justify-center gap-6 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-700 px-6 py-16 text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
              <span className="material-symbols-outlined text-4xl text-primary">upload_file</span>
            </div>
            <div className="flex flex-col gap-2">
              <p className="text-lg font-bold text-gray-900 dark:text-white">Upload Soil Test Card</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Upload your government or market soil test card for automatic data extraction
              </p>
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              id="soil-card-upload"
            />
            <label
              htmlFor="soil-card-upload"
              className="mt-2 rounded-lg bg-primary/20 dark:bg-primary/30 px-6 py-3 text-sm font-bold text-primary cursor-pointer"
            >
              Choose Soil Card Image
            </label>
            {selectedFile && (
              <div className="mt-4 p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-green-800 dark:text-green-200">
                  Selected: {selectedFile.name}
                </p>
              </div>
            )}
          </div>

          {/* Process Button */}
          {selectedFile && !extractedData && (
            <button 
              className="w-full rounded-lg bg-primary py-3 text-base font-bold text-white shadow-lg shadow-primary/30 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={processSoilCard}
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing Soil Card...' : 'Extract Data from Card'}
            </button>
          )}

          {/* Extracted Data Display */}
          {extractedData && (
            <div className="bg-white dark:bg-gray-800/50 rounded-xl p-4 shadow-sm">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                📊 Extracted Soil Data
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Nitrogen (N):</span>
                  <span className="font-semibold">{extractedData.N} ppm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Phosphorus (P):</span>
                  <span className="font-semibold">{extractedData.P} ppm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Potassium (K):</span>
                  <span className="font-semibold">{extractedData.K} ppm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">pH Level:</span>
                  <span className="font-semibold">{extractedData.ph}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Organic Matter:</span>
                  <span className="font-semibold">{extractedData.organicMatter}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Moisture:</span>
                  <span className="font-semibold">{extractedData.moisture}%</span>
                </div>
              </div>
              
              <button 
                className="w-full mt-4 rounded-lg bg-primary py-3 text-base font-bold text-white"
                onClick={useExtractedData}
              >
                Use This Data for Recommendations
              </button>
            </div>
          )}

          {/* Manual Input Option */}
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-2">Don't have a soil card?</p>
            <button 
              className="text-primary font-medium"
              onClick={() => navigate('/advisory')}
            >
              Enter Data Manually Instead
            </button>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SoilCardUpload;
