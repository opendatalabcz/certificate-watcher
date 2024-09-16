import React, { useState } from 'react';
import API from '../api/axios';

const SearchSettingForm = () => {
    const [domainBase, setDomainBase] = useState('');
    const [tld, setTld] = useState('');
    const [additionalSettings, setAdditionalSettings] = useState('');
    const [logo, setLogo] = useState(null);

    const handleSubmit = async (event) => {
        event.preventDefault();

        const formData = new FormData();
        formData.append('domain_base', domainBase);
        formData.append('tld', tld);
        formData.append('additional_settings', additionalSettings);
        if (logo) {
            formData.append('logo', logo);
        }

        try {
            const response = await API.post('/search-settings/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            console.log('Search setting created:', response.data);
        } catch (error) {
            console.error('Error creating search setting:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={domainBase}
                onChange={(e) => setDomainBase(e.target.value)}
                placeholder="Domain Base"
                required
            />
            <input
                type="text"
                value={tld}
                onChange={(e) => setTld(e.target.value)}
                placeholder="Top Level Domain (TLD)"
                required
            />
            <textarea
                value={additionalSettings}
                onChange={(e) => setAdditionalSettings(e.target.value)}
                placeholder="Additional Settings (JSON format)"
            />
            <input
                type="file"
                onChange={(e) => setLogo(e.target.files[0])}
                accept="image/*"
            />
            <button type="submit">Submit</button>
        </form>
    );
};

export default SearchSettingForm;
