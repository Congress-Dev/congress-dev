import React from "react";
import { Card, Tag, Button, Intent } from "@blueprintjs/core";
import { useHistory } from "react-router-dom";
import "./styles.scss";

const CommitteeCard = ({ committee }) => {
    const history = useHistory();

    const handleViewDetails = () => {
        history.push(`/committee/${committee.legislationCommitteeId}`);
    };

    const getChamberIntent = (chamber) => {
        switch (chamber) {
            case "House":
                return Intent.PRIMARY;
            case "Senate":
                return Intent.SUCCESS;
            default:
                return Intent.NONE;
        }
    };

    return (
        <Card className="committee-card" elevation={1}>
            <div className="committee-header">
                <h3 className="committee-name">{`${committee.parentName ? `${committee.parentName} - ` : ""}${committee.name}`}</h3>
                <div className="committee-tags">
                    {committee.chamber && (
                        <Tag intent={getChamberIntent(committee.chamber)} minimal>
                            {committee.chamber}
                        </Tag>
                    )}
                    {committee.committee_type && (
                        <Tag minimal>
                            {committee.committee_type}
                        </Tag>
                    )}
                </div>
            </div>
            
            <div className="committee-details">
                <div className="committee-info">
                    <p><strong>Congress:</strong> {committee.congressId}</p>
                    {committee.thomasId && (
                        <p><strong>Thomas ID:</strong> {committee.thomasId}</p>
                    )}
                    {committee.systemCode && (
                        <p><strong>System Code:</strong> {committee.system_code}</p>
                    )}
                </div>
                
                {committee.jurisdiction && (
                    <div className="committee-jurisdiction">
                        <p><strong>Jurisdiction:</strong></p>
                        <p className="jurisdiction-text">{committee.jurisdiction}</p>
                    </div>
                )}
            </div>
            
            <div className="committee-actions">
                <Button 
                    intent={Intent.PRIMARY} 
                    onClick={handleViewDetails}
                    small
                >
                    View Details
                </Button>
                {committee.url && (
                    <Button 
                        onClick={() => window.open(committee.url, '_blank')}
                        minimal
                        small
                    >
                        Official Website
                    </Button>
                )}
            </div>
        </Card>
    );
};

export default CommitteeCard; 