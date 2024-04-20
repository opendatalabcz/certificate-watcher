import React from 'react';

const SearchSettingDetailedCard = ({ setting }) => {
    return (
        <div className="card bg-dark text-white mb-3">
            <div className="card-header">{setting.owner} - {setting.tld}</div>
            <div className="card-body">
                <h5 className="card-title">{setting.domain_base}</h5>
                <p className="card-text">Additional Settings: {JSON.stringify(setting.additional_settings)}</p>
            </div>
        </div>
    );
};

export default SearchSettingDetailedCard;