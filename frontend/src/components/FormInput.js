import React from "react";

const FormInput = React.memo(
  ({
    label,
    value,
    onChange,
    type = "text",
    placeholder = "",
    className = "",
    ...props
  }) => (
    <div className={`mb-2 ${className}`}>
      {label && <label className="block mb-1 font-medium">{label}</label>}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="border p-2 rounded w-full"
        {...props}
      />
    </div>
  )
);

FormInput.displayName = "FormInput";

export default FormInput;
