import React, { useState } from "react";
import ImageDetailsTable from "../images/ImageDetailsTable"; // Import the ImageDetailsTable component

const ScanHistoryList = ({ scanHistories }) => {
    const [visibleHistoryId, setVisibleHistoryId] = useState(null); // State to track visible table

    const handleToggleVisibility = (historyId) => {
        // Toggle visibility for the corresponding history
        setVisibleHistoryId((prev) => (prev === historyId ? null : historyId));
    };
    console.log(scanHistories);
    return (
        <div className="scan-history-list">
            {scanHistories.map((history) => (
                <div key={history.id} className="card mb-3">
                    <div className="card-header d-flex justify-content-between align-items-center">
                        <div>
                            <h5>Scan at {history.scan_time}</h5>
                            <p>{history.notes}</p>
                        </div>
                        <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleToggleVisibility(history.id)}
                        >
                            {visibleHistoryId === history.id ? "Hide Images" : "Show Images"}
                        </button>
                    </div>
                    {visibleHistoryId === history.id && (
                        <div className="card-body">
                            <ImageDetailsTable images={history.images} />
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};
export default ScanHistoryList;