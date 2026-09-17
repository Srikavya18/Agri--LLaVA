import { useCallback, useRef, useState } from "react";
import { ImagePlus, X } from "lucide-react";
import { validateImageFile } from "../utils/imageValidation";

interface ImageUploaderProps {
  image: File | null;
  onImageSelected: (file: File) => void;
  onImageRemoved: () => void;
  onValidationError: (message: string) => void;
}

export function ImageUploader({
  image,
  onImageSelected,
  onImageRemoved,
  onValidationError,
}: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (file: File) => {
      const result = validateImageFile(file);
      if (!result.valid) {
        onValidationError(result.error ?? "This image can't be used. Please try another.");
        return;
      }
      setPreviewUrl(URL.createObjectURL(file));
      onImageSelected(file);
    },
    [onImageSelected, onValidationError],
  );

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const handleRemove = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    onImageRemoved();
    if (inputRef.current) inputRef.current.value = "";
  };

  if (image && previewUrl) {
    return (
      <div className="relative rounded-card overflow-hidden border border-leaf-light bg-white">
        <img src={previewUrl} alt="Selected crop leaf" className="w-full max-h-80 object-contain" />
        <button
          type="button"
          onClick={handleRemove}
          className="absolute top-3 right-3 bg-white/90 hover:bg-white text-ink rounded-full p-2 border border-leaf-light shadow-none transition-colors"
          aria-label="Remove image"
        >
          <X size={18} />
        </button>
      </div>
    );
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`rounded-card border-2 border-dashed p-10 text-center transition-colors ${
        isDragging ? "border-leaf bg-leaf-light" : "border-leaf-light bg-white"
      }`}
    >
      <div className="flex flex-col items-center gap-3">
        <div className="rounded-full bg-leaf-light p-3 text-forest">
          <ImagePlus size={28} strokeWidth={1.8} />
        </div>
        <p className="font-body text-ink">Drag & drop your crop image here</p>
        <p className="text-sm text-ink-soft">JPEG, PNG, or WEBP · up to 10 MB</p>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="mt-2 rounded-full bg-forest text-paper px-5 py-2 text-sm font-medium hover:bg-leaf-dark transition-colors"
        >
          Choose Image
        </button>
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
      </div>
    </div>
  );
}
