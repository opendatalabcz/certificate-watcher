import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";

const CreateSearchSettingPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        domain_base: "",
        tld: "",
        additional_settings: "",
        logo_url: "",
    });
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Parse additional_settings into an object if provided
            const parsedSettings = formData.additional_settings
                ? JSON.parse(formData.additional_settings)
                : null;

            const payload = {
                domain_base: formData.domain_base,
                tld: formData.tld,
                additional_settings: parsedSettings,
                logo_url: formData.logo_url || null,
            };

            await API.post("/search-settings/", payload);
            navigate("/search-settings"); // Navigate to the list of search settings
        } catch (err) {
            console.error("Error creating search setting:", err);
            setError("Failed to create search setting. Please check your input.");
        }
    };

    return (
        <div className="container mt-4">
            <h1>Create Search Setting</h1>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="domain_base" className="form-label">
                        Domain Base
                    </label>
                    <input
                        type="text"
                        className="form-control"
                        id="domain_base"
                        name="domain_base"
                        value={formData.domain_base}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="tld" className="form-label">
                        Top-Level Domain (TLD)
                    </label>
                    <input
                        type="text"
                        className="form-control"
                        id="tld"
                        name="tld"
                        value={formData.tld}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="additional_settings" className="form-label">
                        Additional Settings (JSON Format)
                    </label>
                    <textarea
                        className="form-control"
                        id="additional_settings"
                        name="additional_settings"
                        value={formData.additional_settings}
                        onChange={handleChange}
                        placeholder='{"key1": "value1", "key2": "value2"}'
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="logo_url" className="form-label">
                        Logo URL
                    </label>
                    <input
                        type="url"
                        className="form-control"
                        id="logo_url"
                        name="logo_url"
                        value={formData.logo_url}
                        onChange={handleChange}
                    />
                </div>
                <button type="submit" className="btn btn-primary">
                    Create Search Setting
                </button>
            </form>
        </div>
    );
};

export default CreateSearchSettingPage;
