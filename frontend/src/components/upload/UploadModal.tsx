"use client";

import { useState, useRef } from "react";
import { UploadCloud, X, File as FileIcon, CheckCircle2 } from "lucide-react";
import { useUpload } from "@/features/documents/hooks";
import { useUIStore } from "@/stores/ui-store";

export default function UploadModal() {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const { toggleUploadModal } = useUIStore();
  const { mutate: uploadFile, isPending, isSuccess } = useUpload();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (!file) return;
    uploadFile({ file });
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0F172A] border border-gray-800 rounded-2xl w-full max-w-md overflow-hidden relative shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800/60">
          <h2 className="text-sm font-semibold text-white">Upload Knowledge</h2>
          <button 
            onClick={toggleUploadModal}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {isSuccess ? (
            <div className="flex flex-col items-center justify-center space-y-4 py-8">
              <div className="w-16 h-16 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <p className="text-gray-200 font-medium">Upload successful!</p>
              <p className="text-xs text-gray-400 text-center max-w-xs">
                Your document has been processed and is now available for RAG queries.
              </p>
            </div>
          ) : (
            <>
              {/* Dropzone */}
              <div
                className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-colors ${
                  dragActive 
                    ? "border-blue-500 bg-blue-500/5 text-blue-400" 
                    : file 
                      ? "border-gray-700 bg-[#1E293B]/50" 
                      : "border-gray-700 hover:border-gray-600 hover:bg-[#1E293B] text-gray-400"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
              >
                <input
                  ref={inputRef}
                  type="file"
                  multiple={false}
                  onChange={handleChange}
                  className="hidden"
                />
                
                {file ? (
                  <>
                    <FileIcon className="w-10 h-10 mb-3 text-blue-400" />
                    <p className="text-sm font-medium text-white break-all line-clamp-1">{file.name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {(file.size / 1024 / 1024).toFixed(2)} MB • Click to change
                    </p>
                  </>
                ) : (
                  <>
                    <UploadCloud className="w-10 h-10 mb-3" />
                    <p className="text-sm font-medium text-gray-300">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                      PDF, TXT, DOCX, MD (Max 50MB)
                    </p>
                  </>
                )}
              </div>

              {/* Action */}
              <button
                disabled={!file || isPending}
                onClick={handleUpload}
                className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 rounded-lg py-3 text-sm font-medium transition-colors flex items-center justify-center cursor-pointer disabled:cursor-not-allowed"
              >
                {isPending ? "Uploading..." : "Upload Document"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
