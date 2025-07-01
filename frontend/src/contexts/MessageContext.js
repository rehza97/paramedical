import React, { createContext, useContext, useState, useCallback } from "react";

const MessageContext = createContext();

export const MessageProvider = ({ children }) => {
  const [message, setMessage] = useState(null);
  const [type, setType] = useState("success");
  const [loading, setLoading] = useState(false);

  const showMessage = useCallback((text, type = "success") => {
    setMessage(text);
    setType(type);
    setTimeout(() => setMessage(null), 3000);
  }, []);

  return (
    <MessageContext.Provider
      value={{ message, type, showMessage, loading, setLoading }}
    >
      {children}
    </MessageContext.Provider>
  );
};

export const useMessage = () => useContext(MessageContext);
