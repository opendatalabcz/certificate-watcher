import React, { useEffect, useState } from 'react';
import API from '../api/axios';
import { useParams } from 'react-router-dom';

import FlaggedDataCard from './FlaggedDataCard';
import ImageDetailsTable from './ImageDetailsTable';

const FlaggedDataDetailPage = () => {
    const { id: dataId } = useParams();
    const [dataDetail, setDataDetail] = useState(null);

    useEffect(() => {
        const fetchDataDetail = async () => {
            try {
                const { data } = await API.get(`/flagged-data/${dataId}/`);
                setDataDetail(data);
            } catch (error) {
                console.error('Failed to fetch flagged data details:', error);
            }
        };

        fetchDataDetail();
    }, [dataId]);

    if (!dataDetail) {
        return <div className="text-center">Loading...</div>;
    }

    return (
        <div className="container mt-4">
            <FlaggedDataCard data={dataDetail} />
            <ImageDetailsTable images={dataDetail.images} />
        </div>
    );
};

export default FlaggedDataDetailPage;