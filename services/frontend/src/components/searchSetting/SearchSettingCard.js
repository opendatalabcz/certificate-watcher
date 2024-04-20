import React from 'react';
import { Link } from 'react-router-dom';

const SearchSettingCard = ({ setting }) => {
    return (
        <div className="card bg-dark text-white mb-3">
            <div className="card-header">{setting.owner}</div>
            <div className="card-body">
                <h5 className="card-title">{setting.domain_base}.{setting.tld}</h5>
                <p className="card-text">Flagged Data Count: {setting.flagged_data_count}</p>
                {/* Link to the detail page */}
                <Link to={`/search-settings/${setting?.id}`} className="btn btn-light">View Details</Link>
            </div>
        </div>
    );
};

export default SearchSettingCard;