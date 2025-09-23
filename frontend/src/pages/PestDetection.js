import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const PestDetection = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [detectionResult, setDetectionResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setDetectionResult(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);

    // Simulate realistic pest detection with multiple possible results
    setTimeout(() => {
      const pestDatabase = [
        {
          pestName: 'Brown Planthopper (BPH)',
          confidence: 0.92,
          description: 'Brown planthopper is a major pest of rice crops in India. It causes hopperburn by sucking plant sap and can transmit viral diseases like grassy stunt virus.',
          treatment: 'Use resistant rice varieties like TN1, IR36. Apply neem-based insecticides. Maintain proper water management and avoid excessive nitrogen fertilization.',
          severity: 'High',
          cropAffected: 'Rice',
          symptoms: ['Yellowing of leaves', 'Stunted growth', 'Hopperburn patches', 'Plant death in severe cases'],
          prevention: ['Use resistant varieties', 'Balanced fertilization', 'Proper water management', 'Remove weeds'],
          organicTreatment: 'Neem oil spray (3ml/L), Beauveria bassiana application',
          chemicalTreatment: 'Imidacloprid 17.8% SL @ 0.3ml/L or Thiamethoxam 25% WG @ 0.2g/L',
          image: 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=400'
        },
        {
          pestName: 'Aphids (Green Peach Aphid)',
          confidence: 0.89,
          description: 'Aphids are small, soft-bodied insects that feed on plant sap. They can cause leaf curling, yellowing, and transmit viral diseases in various crops.',
          treatment: 'Spray neem oil or insecticidal soap. Introduce beneficial insects like ladybugs and lacewings. Use reflective mulches.',
          severity: 'Medium',
          cropAffected: 'Tomato, Potato, Cotton',
          symptoms: ['Leaf curling', 'Yellowing of leaves', 'Sticky honeydew', 'Sooty mold growth'],
          prevention: ['Regular monitoring', 'Remove infected plants', 'Use yellow sticky traps', 'Encourage natural predators'],
          organicTreatment: 'Neem oil (5ml/L), Soap solution spray, Garlic-chili extract',
          chemicalTreatment: 'Acetamiprid 20% SP @ 0.2g/L or Dimethoate 30% EC @ 2ml/L',
          image: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400'
        },
        {
          pestName: 'Bollworm (American Bollworm)',
          confidence: 0.94,
          description: 'American bollworm is a polyphagous pest affecting cotton, tomato, chickpea, and other crops. Larvae bore into fruits and bolls causing significant yield loss.',
          treatment: 'Use pheromone traps for monitoring. Apply Bt-based biopesticides. Practice crop rotation and intercropping with marigold.',
          severity: 'High',
          cropAffected: 'Cotton, Tomato, Chickpea',
          symptoms: ['Holes in fruits/bolls', 'Frass near entry holes', 'Damaged flowers', 'Yield reduction'],
          prevention: ['Pheromone traps', 'Crop rotation', 'Intercropping with marigold', 'Deep summer plowing'],
          organicTreatment: 'Bt spray (1g/L), NPV application, Trichogramma release',
          chemicalTreatment: 'Chlorantraniliprole 18.5% SC @ 0.3ml/L or Flubendiamide 480% SC @ 0.2ml/L',
          image: 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=400'
        },
        {
          pestName: 'Whitefly (Bemisia tabaci)',
          confidence: 0.87,
          description: 'Whiteflies are tiny flying insects that feed on plant sap and transmit viral diseases. They are major pests of cotton, tomato, and other vegetable crops.',
          treatment: 'Use yellow sticky traps. Apply neem-based products. Maintain field hygiene and remove crop residues.',
          severity: 'Medium',
          cropAffected: 'Cotton, Tomato, Brinjal',
          symptoms: ['Yellowing of leaves', 'Leaf curling', 'Honeydew secretion', 'Viral disease transmission'],
          prevention: ['Yellow sticky traps', 'Reflective mulches', 'Crop rotation', 'Weed management'],
          organicTreatment: 'Neem oil (5ml/L), Beauveria bassiana, Sticky traps',
          chemicalTreatment: 'Thiamethoxam 25% WG @ 0.2g/L or Spiromesifen 22.9% SC @ 1ml/L',
          image: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400'
        }
      ];

      // Randomly select a pest for demonstration
      const randomPest = pestDatabase[Math.floor(Math.random() * pestDatabase.length)];

      setDetectionResult(randomPest);
      setIsAnalyzing(false);
    }, 3000);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Low':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'Medium':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'High':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  return (
    <div className="relative flex h-auto min-h-screen w-full flex-col justify-between overflow-x-hidden">
      <main className="flex-grow">
        <header className="flex items-center p-4">
          <button
            className="text-gray-800 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full p-2 transition-colors"
            onClick={() => navigate('/')}
          >
            <span className="material-symbols-outlined text-3xl">arrow_back</span>
          </button>
          <h1 className="flex-1 text-center text-xl font-bold text-gray-900 dark:text-white pr-8">🐛 Pest Detection</h1>
        </header>

        <div className="p-4">
          <div className="flex flex-col items-center justify-center gap-6 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-700 px-6 py-16 text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
              <span className="material-symbols-outlined text-4xl text-primary">cloud_upload</span>
            </div>
            <div className="flex flex-col gap-2">
              <p className="text-lg font-bold text-gray-900 dark:text-white">Upload Image</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Drag and drop or click to upload an image.</p>
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="mt-2 rounded-lg bg-primary/20 dark:bg-primary/30 px-6 py-3 text-sm font-bold text-primary cursor-pointer"
            >
              Browse Files
            </label>
            {selectedFile && (
              <div className="mt-4 p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-green-800 dark:text-green-200">
                  Selected: {selectedFile.name}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="px-4 pb-4">
          <button 
            className="w-full rounded-lg bg-primary py-3 text-base font-bold text-white shadow-lg shadow-primary/30 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleSubmit}
            disabled={!selectedFile || isAnalyzing}
          >
            {isAnalyzing ? 'Analyzing Image...' : 'Submit for Detection'}
          </button>
        </div>

        {/* Detection Results */}
        {detectionResult && (
          <div className="px-4 pt-6 pb-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">🔍 Pest Analysis Report</h2>

            {/* Main Pest Info */}
            <div className="rounded-xl bg-white dark:bg-gray-800/50 p-4 shadow-sm mb-4">
              <div className="flex items-start gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-sm font-medium text-primary">Detected Pest</p>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(detectionResult.severity)}`}>
                      {detectionResult.severity} Risk
                    </span>
                  </div>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">{detectionResult.pestName}</p>
                  <p className="text-sm text-primary font-medium">Crop Affected: {detectionResult.cropAffected}</p>
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    {detectionResult.description}
                  </p>

                  <div className="mt-3 flex items-center gap-4">
                    <div className="text-center">
                      <p className="text-xs text-gray-500">Confidence</p>
                      <p className="text-lg font-bold text-primary">
                        {(detectionResult.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-gray-500">Risk Level</p>
                      <p className={`text-sm font-bold ${detectionResult.severity === 'High' ? 'text-red-600' : detectionResult.severity === 'Medium' ? 'text-yellow-600' : 'text-green-600'}`}>
                        {detectionResult.severity}
                      </p>
                    </div>
                  </div>
                </div>
                <div
                  className="w-24 h-24 flex-shrink-0 rounded-lg bg-cover bg-center border-2 border-gray-200 dark:border-gray-700"
                  style={{ backgroundImage: `url("${detectionResult.image}")` }}
                ></div>
              </div>
            </div>

            {/* Symptoms */}
            <div className="rounded-xl bg-white dark:bg-gray-800/50 p-4 shadow-sm mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">🌿 Symptoms to Look For</h3>
              <div className="grid grid-cols-1 gap-2">
                {detectionResult.symptoms.map((symptom, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{symptom}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Treatment Options */}
            <div className="rounded-xl bg-white dark:bg-gray-800/50 p-4 shadow-sm mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">💊 Treatment Options</h3>

              <div className="space-y-3">
                <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
                  <h4 className="font-medium text-green-800 dark:text-green-200 mb-1">🌱 Organic Treatment</h4>
                  <p className="text-sm text-green-700 dark:text-green-300">{detectionResult.organicTreatment}</p>
                </div>

                <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                  <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-1">🧪 Chemical Treatment</h4>
                  <p className="text-sm text-blue-700 dark:text-blue-300">{detectionResult.chemicalTreatment}</p>
                </div>
              </div>
            </div>

            {/* Prevention */}
            <div className="rounded-xl bg-white dark:bg-gray-800/50 p-4 shadow-sm">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">🛡️ Prevention Measures</h3>
              <div className="grid grid-cols-1 gap-2">
                {detectionResult.prevention.map((measure, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{measure}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default PestDetection;
