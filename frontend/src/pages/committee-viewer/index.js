import React, { useState, useEffect } from "react";
import { useParams, useHistory } from "react-router-dom";
import {
    Card,
    Elevation,
    Tag,
    Button,
    Intent,
    Spinner,
    NonIdealState,
    Divider,
    Callout,
    HTMLTable,
} from "@blueprintjs/core";

import { getCommitteeById, getSubcommittees } from "common/api";
import CommitteeCard from "components/committee-card";
import "./styles.scss";

function CommitteeViewer() {
    const { committeeId } = useParams();
    const history = useHistory();
    const [committee, setCommittee] = useState(null);
    const [subcommittees, setSubcommittees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [subcommitteesLoading, setSubcommitteesLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (committeeId) {
            fetchCommitteeDetails();
        }
    }, [committeeId]);

    const fetchCommitteeDetails = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const committeeData = await getCommitteeById(committeeId);
            if (committeeData) {
                setCommittee(committeeData);
                
                // Fetch subcommittees if this is a parent committee
                if (!committeeData.parent_id) {
                    setSubcommitteesLoading(true);
                    try {
                        const subcommitteeData = await getSubcommittees(committeeId);
                        setSubcommittees(subcommitteeData || []);
                    } catch (subError) {
                        console.error("Error fetching subcommittees:", subError);
                        setSubcommittees([]);
                    } finally {
                        setSubcommitteesLoading(false);
                    }
                }
            } else {
                setError("Committee not found");
            }
        } catch (err) {
            console.error("Error fetching committee:", err);
            setError("Failed to load committee information");
        } finally {
            setLoading(false);
        }
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

    const handleBackToSearch = () => {
        history.push("/committees");
    };

    if (loading) {
        return (
            <div className="committee-viewer-loading">
                <Spinner size={50} />
                <p>Loading committee information...</p>
            </div>
        );
    }

    if (error || !committee) {
        return (
            <div className="committee-viewer-error">
                <NonIdealState
                    icon="error"
                    title="Committee Not Found"
                    description={error || "The requested committee could not be found."}
                    action={
                        <Button
                            intent={Intent.PRIMARY}
                            onClick={handleBackToSearch}
                            icon="arrow-left"
                        >
                            Back to Committee Search
                        </Button>
                    }
                />
            </div>
        );
    }

    return (
        <div className="committee-viewer">
            <div className="committee-viewer-header">
                <Button
                    minimal
                    icon="arrow-left"
                    onClick={handleBackToSearch}
                    className="back-button"
                >
                    Back to Search
                </Button>
            </div>

            <Card elevation={Elevation.TWO} className="committee-main-card">
                <div className="committee-title-section">
                    <div className="committee-title">
                        <h1>{committee.name}</h1>
                        <div className="committee-main-tags">
                            {committee.chamber && (
                                <Tag
                                    intent={getChamberIntent(committee.chamber)}
                                    large
                                >
                                    {committee.chamber}
                                </Tag>
                            )}
                            {committee.committee_type && (
                                <Tag large minimal>
                                    {committee.committee_type}
                                </Tag>
                            )}
                            {committee.parent_id && (
                                <Tag intent={Intent.WARNING} large>
                                    Subcommittee
                                </Tag>
                            )}
                        </div>
                    </div>
                </div>

                <Divider />

                <div className="committee-details-grid">
                    <div className="committee-basic-info">
                        <h3>Basic Information</h3>
                        <HTMLTable striped className="info-table">
                            <tbody>
                                <tr>
                                    <td><strong>Congress</strong></td>
                                    <td>{committee.congress_id}</td>
                                </tr>
                                {committee.thomas_id && (
                                    <tr>
                                        <td><strong>Thomas ID</strong></td>
                                        <td>{committee.thomas_id}</td>
                                    </tr>
                                )}
                                {committee.committee_id && (
                                    <tr>
                                        <td><strong>Committee ID</strong></td>
                                        <td>{committee.committee_id}</td>
                                    </tr>
                                )}
                                {committee.system_code && (
                                    <tr>
                                        <td><strong>System Code</strong></td>
                                        <td>{committee.system_code}</td>
                                    </tr>
                                )}
                            </tbody>
                        </HTMLTable>
                    </div>

                    <div className="committee-contact-info">
                        <h3>Contact Information</h3>
                        <div className="contact-details">
                            {committee.address && (
                                <div className="contact-item">
                                    <strong>Address:</strong>
                                    <p>{committee.address}</p>
                                </div>
                            )}
                            {committee.phone && (
                                <div className="contact-item">
                                    <strong>Phone:</strong>
                                    <p>{committee.phone}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {committee.jurisdiction && (
                    <>
                        <Divider />
                        <div className="committee-jurisdiction-section">
                            <h3>Jurisdiction</h3>
                            <Callout intent={Intent.NONE} className="jurisdiction-callout">
                                {committee.jurisdiction}
                            </Callout>
                        </div>
                    </>
                )}

                <Divider />

                <div className="committee-links-section">
                    <h3>External Links</h3>
                    <div className="committee-links">
                        {committee.url && (
                            <Button
                                intent={Intent.PRIMARY}
                                onClick={() => window.open(committee.url, '_blank')}
                                icon="link"
                            >
                                Official Website
                            </Button>
                        )}
                        {committee.minority_url && (
                            <Button
                                onClick={() => window.open(committee.minority_url, '_blank')}
                                icon="link"
                                minimal
                            >
                                Minority Website
                            </Button>
                        )}
                        {committee.rss_url && (
                            <Button
                                onClick={() => window.open(committee.rss_url, '_blank')}
                                icon="feed"
                                minimal
                            >
                                RSS Feed
                            </Button>
                        )}
                        {committee.youtube_id && (
                            <Button
                                onClick={() => window.open(`https://youtube.com/channel/${committee.youtube_id}`, '_blank')}
                                icon="video"
                                minimal
                            >
                                YouTube Channel
                            </Button>
                        )}
                    </div>
                </div>
            </Card>

            {!committee.parent_id && (
                <div className="subcommittees-section">
                    <Card elevation={Elevation.ONE}>
                        <h2>Subcommittees</h2>
                        {subcommitteesLoading ? (
                            <div className="subcommittees-loading">
                                <Spinner size={30} />
                                <p>Loading subcommittees...</p>
                            </div>
                        ) : subcommittees.length > 0 ? (
                            <div className="subcommittees-list">
                                {subcommittees.map((subcommittee) => (
                                    <CommitteeCard
                                        key={subcommittee.legislation_committee_id}
                                        committee={subcommittee}
                                    />
                                ))}
                            </div>
                        ) : (
                            <NonIdealState
                                icon="folder-open"
                                title="No Subcommittees"
                                description="This committee does not have any subcommittees."
                            />
                        )}
                    </Card>
                </div>
            )}
        </div>
    );
}

export default CommitteeViewer; 