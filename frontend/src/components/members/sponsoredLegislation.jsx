import React from 'react';
import { Link } from 'react-router-dom';

const SponsoredLegislation = ({
  session,
  cosponsored,
  chamber,
  number,
  version,
  title
}) => {
  const billPrefix = chamber === 'House' ? 'H.R' : 'S';

  return (
    <div className="legislation-card">
      <h2>{billPrefix} {number}</h2>
      <p>{title}</p>
      <p><strong>Cosponsored:</strong> {cosponsored ? 'Yes' : 'No'}</p>
      <Link to={`/bill/${session}/${chamber}/${number}/${version}`}>
        More Details
      </Link>
    </div>
  );
};

export default SponsoredLegislation;