import React from 'react';
import { Link } from 'react-router-dom';

const FlaggedDataList = ({ flaggedData }) => {
    console.log(flaggedData);
    return (
        <table className="table table-dark">
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>Algorithm</th>
                    <th>Flagged Time</th>
                    <th>Successfully Scraped</th>
                    <th>Suspected Logo</th>
                    <th>Scraped Images Count</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {flaggedData.map(fd => (
                    <tr key={fd.id}>
                        <td>{fd.domain}</td>
                        <td>{fd.algorithm}</td>
                        <td>{fd.flagged_time}</td>
                        <td>{fd.successfully_scraped ? 'Yes' : 'No'}</td>
                        <td>{fd.suspected_logo ? 'Yes' : 'No'}</td>
                        <td>{fd.scraped_images_count}</td>
                        <td><Link to={`/flagged-data/${fd?.id}/`}>View</Link></td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default FlaggedDataList;