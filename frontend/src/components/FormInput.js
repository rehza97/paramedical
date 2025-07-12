import React from "react";

const FormInput = React.memo(
  ({
    label,
    value,
    onChange,
    type = "text",
    placeholder = "",
    className = "",
    options = [], // for select
    ...props
  }) => (
    <div className={`mb-2 ${className}`}>
      {label && <label className="block mb-1 font-medium">{label}</label>}
      {type === "select" ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="border p-2 rounded w-full"
          {...props}
        >
          <option value="">{placeholder || "Select an option"}</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="border p-2 rounded w-full"
          {...props}
        />
      )}
    </div>
  )
);

FormInput.displayName = "FormInput";

export default FormInput;
