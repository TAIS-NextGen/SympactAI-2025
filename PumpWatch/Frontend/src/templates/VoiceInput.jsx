import React, { useState, useRef, useEffect } from "react";
import {
  Mic,
  MicOff,
  Upload,
  Play,
  Pause,
  Trash2,
  Download,
  AlertTriangle,
} from "lucide-react";

export default function VoiceInputComponent() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevels, setAudioLevels] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioRef = useRef(null);
  const streamRef = useRef(null);
  const analyzerRef = useRef(null);
  const animationRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    setAudioLevels(new Array(40).fill(0));
  }, []);

  const startRecording = async () => {
    try {
      setResult(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      const source = audioContext.createMediaStreamSource(stream);
      const analyzer = audioContext.createAnalyser();
      analyzer.fftSize = 256;
      source.connect(analyzer);
      analyzerRef.current = { analyzer, audioContext };

      visualizeAudio();

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/wav" });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stopVisualization();
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      intervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error("Error starting recording:", error);
      alert("Error accessing microphone. Please allow microphone access.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      streamRef.current.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
      clearInterval(intervalRef.current);
    }
  };

  const visualizeAudio = () => {
    if (analyzerRef.current) {
      const { analyzer } = analyzerRef.current;
      const dataArray = new Uint8Array(analyzer.frequencyBinCount);

      const animate = () => {
        analyzer.getByteFrequencyData(dataArray);

        const levels = [];
        const binSize = Math.floor(dataArray.length / 40);

        for (let i = 0; i < 40; i++) {
          let sum = 0;
          for (let j = 0; j < binSize; j++) sum += dataArray[i * binSize + j];
          levels.push(sum / binSize / 255);
        }

        setAudioLevels(levels);
        animationRef.current = requestAnimationFrame(animate);
      };

      animate();
    }
  };

  const stopVisualization = () => {
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
    if (analyzerRef.current) analyzerRef.current.audioContext.close();
    setAudioLevels(new Array(40).fill(0));
  };

  const playAudio = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const pauseAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const deleteRecording = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setIsPlaying(false);
    setRecordingTime(0);
    setResult(null);
  };

  const downloadAudio = () => {
    if (audioBlob) {
      const url = URL.createObjectURL(audioBlob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `voice-recording-${Date.now()}.wav`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const processAudio = async () => {
    if (!audioBlob) return;
    setIsProcessing(true);
    try {
      const formData = new FormData();
      const filename = `voice-recording-${Date.now()}.wav`;
      formData.append("audio", audioBlob, filename);
      await new Promise((resolve) => setTimeout(resolve, 2000));
      const mockClassifications = [
        "Speech",
        "Music",
        "Noise",
        "Silence",
        "Nature",
        "Urban",
        "Human Voice",
        "Animal Sound",
      ];
      const randomClassification =
        mockClassifications[
          Math.floor(Math.random() * mockClassifications.length)
        ];
      setResult({
        Prediction: randomClassification,
        Message: `${filename} uploaded successfully`,
      });
    } catch (error) {
      console.error(error);
      setResult({
        Prediction: "Error",
        Message: "Failed to process audio file",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white p-8 rounded-2xl shadow-lg space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Audio Classification System
        </h1>
        <p className="text-gray-600">
          Record your pump sounds and get AI-powered classification results
        </p>
      </div>
      {result ? (
        // Show this when result exists
        <div className="bg-gray-50 p-6 rounded-xl shadow-md border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Upload className="w-5 h-5 text-green-500" />
            <span>Classification Result</span>
          </h3>
          <div className="bg-gray-100 rounded-lg p-4 font-mono text-sm text-gray-800">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <span>Abnormal Pump Sound Detected</span>
            </div>
          </div>
        </div>
      ) : (
        // Show this when result doesn't exist
        <div className="flex items-end justify-center space-x-1 h-32 bg-gray-100 rounded-xl p-4">
          {audioLevels.map((level, index) => (
            <div
              key={index}
              className="bg-gradient-to-t from-indigo-500 to-purple-500 rounded-sm transition-all duration-100 ease-out"
              style={{
                height: `${Math.max(4, level * 100)}px`,
                width: "6px",
                opacity: isRecording ? 0.9 : 0.3,
              }}
            />
          ))}
        </div>
      )}

      {/* Timer */}
      {(isRecording || audioBlob) && (
        <div className="text-center text-xl font-mono text-gray-800">
          {formatTime(recordingTime)}
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-col items-center space-y-4">
        {/* Record Button */}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`p-6 rounded-full transition-all duration-300 ${
            isRecording
              ? "bg-red-500 hover:bg-red-600 animate-pulse"
              : "bg-indigo-500 hover:bg-indigo-600"
          } shadow-lg`}
        >
          {isRecording ? (
            <MicOff className="w-8 h-8 text-white" />
          ) : (
            <Mic className="w-8 h-8 text-white" />
          )}
        </button>
        <p className="text-gray-700">
          {isRecording
            ? "Recording... Click to stop"
            : "Click to start recording"}
        </p>

        {/* Playback and actions */}
        {audioBlob && (
          <div className="flex space-x-4">
            <button
              onClick={isPlaying ? pauseAudio : playAudio}
              className="p-3 bg-blue-500 hover:bg-blue-600 rounded-full"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5 text-white" />
              ) : (
                <Play className="w-5 h-5 text-white" />
              )}
            </button>
            <button
              onClick={downloadAudio}
              className="p-3 bg-green-500 hover:bg-green-600 rounded-full"
            >
              <Download className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={deleteRecording}
              className="p-3 bg-red-500 hover:bg-red-600 rounded-full"
            >
              <Trash2 className="w-5 h-5 text-white" />
            </button>
          </div>
        )}

        {/* Process Button */}
        {audioBlob && !result && (
          <button
            onClick={processAudio}
            disabled={isProcessing}
            className="px-8 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white font-semibold rounded-lg transition-all duration-300"
          >
            {isProcessing ? "Processing..." : "Classify Audio"}
          </button>
        )}
      </div>

      {/* Hidden audio element */}
      {audioUrl && (
        <audio
          ref={audioRef}
          src={audioUrl}
          onEnded={() => setIsPlaying(false)}
        />
      )}

      {/* Results Display */}
    </div>
  );
}
