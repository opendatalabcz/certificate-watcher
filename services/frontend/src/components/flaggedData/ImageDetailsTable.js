import React from 'react';
import useImageUrls from '../images/useImageUrls';

const ImageDetailsTable = ({ images }) => {
    const imageUrls = useImageUrls(images);

    return (
        <table className="table table-dark table-striped">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Format</th>
                    <th>Uploaded</th>
                    <th>Note</th>
                    <th>Preview</th>
                </tr>
            </thead>
            <tbody>
                {images.map((img) => (
                    <tr key={img.id}>
                        <td>{img.name}</td>
                        <td>{img.format || "N/A"}</td>
                        <td>{new Date(img.created).toLocaleDateString()}</td>
                        <td>{img.note || "None"}</td>
                        <td>
                            {img.local_path ? (
                                <img 
                                    src={imageUrls[img.id] || "path_to_default_image.jpg"}  // Use the blob URL or a default image
                                    alt={img.name} 
                                    style={{ width: "100px", height: "100px" }}
                                />
                            ) : "No local image"}
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default ImageDetailsTable;