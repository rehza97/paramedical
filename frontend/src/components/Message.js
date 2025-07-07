import React from "react";

const Message = ({ text, type = "success" }) => {
  if (!text) return null;

  const getMessageClasses = (type) => {
    switch (type) {
      case "error":
        return "mb-2 p-2 rounded bg-red-100 text-red-700 border border-red-300";
      case "info":
        return "mb-2 p-2 rounded bg-blue-100 text-blue-700 border border-blue-300";
      default:
        return "mb-2 p-2 rounded bg-green-100 text-green-700 border border-green-300";
    }
  };

  return <div className={getMessageClasses(type)}>{text}</div>;
};

export default Message;
