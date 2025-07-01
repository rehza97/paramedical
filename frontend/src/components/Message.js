import React from "react";

const Message = ({ text, type = "success" }) => {
  if (!text) return null;
  let color = "green";
  if (type === "error") color = "red";
  if (type === "info") color = "blue";
  return (
    <div
      className={`mb-2 p-2 rounded bg-${color}-100 text-${color}-700 border border-${color}-300`}
    >
      {text}
    </div>
  );
};

export default Message;
