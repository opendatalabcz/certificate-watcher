import React, { useEffect, useState } from 'react';
import API from '../api/axios';
import { useParams } from 'react-router-dom';
import SearchSettingDetailedCard from './SearchSettingDetailedCard';
import FlaggedDataList from '../flaggedData/FlaggedDataList';

const SearchSettingDetailPage = () => {
    const {id: settingId } = useParams();
    const [settingDetail, setSettingDetail] = useState(null);

    useEffect(() => {
        const fetchSettingDetail = async () => {
            try {
                const { data } = await API.get(`/search-settings/${settingId}`);
                setSettingDetail(data);
            } catch (error) {
                console.error('Failed to fetch setting details:', error);
            }
        };

        fetchSettingDetail();
    }, [settingId]);

    if (!settingDetail) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <SearchSettingDetailedCard setting={settingDetail} />
            <FlaggedDataList flaggedData={settingDetail.flagged_data} />
        </div>
    );
};

export default SearchSettingDetailPage;