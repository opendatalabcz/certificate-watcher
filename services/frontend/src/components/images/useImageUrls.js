import { useState, useEffect } from 'react';
import API from '../api/axios';  // Ensure this is correctly pointing to your Axios configuration

const useImageUrls = (images) => {
    const [imageUrls, setImageUrls] = useState({});

    useEffect(() => {
        const fetchImages = async () => {
            let newImageUrls = {};
            for (let img of images) {
                if (img.local_path) {
                    const imagePath = `/files/${encodeURIComponent(img.local_path)}/${encodeURIComponent(img.name)}.${encodeURIComponent(img.format.toLowerCase())}`;
                    try {
                        const response = await API.get(imagePath, { responseType: 'blob' });
                        const blobUrl = URL.createObjectURL(response.data);
                        newImageUrls[img.id] = blobUrl;
                    } catch (error) {
                        console.error('Failed to fetch image:', imagePath, error);
                        newImageUrls[img.id] = '';  // or set to a default image path
                    }
                }
            }
            setImageUrls(newImageUrls);
        };

        if (images.length > 0) {
            fetchImages();
        }
    }, [images]);  // Rerun when images prop changes

    return imageUrls;
};

export default useImageUrls;