import React, { useEffect, useRef } from "react";

const Modal = ({ open, onClose, title, children, size = "default" }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    if (open) {
      // Focus the modal when it opens
      modalRef.current?.focus();

      // Prevent body scroll
      document.body.style.overflow = "hidden";

      return () => {
        document.body.style.overflow = "unset";
      };
    }
  }, [open]);

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape" && open) {
        onClose();
      }
    };

    if (open) {
      document.addEventListener("keydown", handleEscape);
      return () => document.removeEventListener("keydown", handleEscape);
    }
  }, [open, onClose]);

  if (!open) return null;

  const getSizeClasses = () => {
    switch (size) {
      case "small":
        return "max-w-sm";
      case "large":
        return "max-w-4xl";
      case "xlarge":
        return "max-w-6xl";
      default:
        return "max-w-lg";
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
    >
      <div
        ref={modalRef}
        className={`bg-white rounded-lg shadow-lg w-full ${getSizeClasses()} p-6 relative max-h-[90vh] overflow-y-auto`}
        onClick={(e) => e.stopPropagation()}
        tabIndex={-1}
      >
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 text-xl z-10"
          aria-label="Fermer"
          type="button"
        >
          &times;
        </button>
        {title && (
          <h2 id="modal-title" className="text-xl font-bold mb-4 pr-8">
            {title}
          </h2>
        )}
        {children}
      </div>
    </div>
  );
};

export default Modal;
