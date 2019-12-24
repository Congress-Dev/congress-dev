export const host = window.location.hostname.indexOf('localhost') == 0 ? 'http://localhost:9090' : 'https://api.congress.dev';
function shallowEqual(objA: mixed, objB: mixed): boolean {
  if (objA === objB) {
    return true;
  }

  if (typeof objA !== 'object' || objA === null ||
    typeof objB !== 'object' || objB === null) {
    return false;
  }

  var keysA = Object.keys(objA);
  var keysB = Object.keys(objB);

  if (keysA.length !== keysB.length) {
    return false;
  }

  // Test for A's keys different from B.
  var bHasOwnProperty = hasOwnProperty.bind(objB);
  for (var i = 0; i < keysA.length; i++) {
    if (!bHasOwnProperty(keysA[i]) || objA[keysA[i]] !== objB[keysA[i]]) {
      return false;
    }
  }

  return true;
}

export const shallowCompare = function shallowCompare(instance, nextProps, nextState) {
  return (
    !shallowEqual(instance.props, nextProps) ||
    !shallowEqual(instance.state, nextState)
  );
}

export const versionToFull = {
  ih: 'Introduced in the House',
  is: 'Introduced in the Senate',

  rfh: 'Referred in House',
  rfs: 'Referred in Senate',

  rds: 'Received in Senate',
  rhs: 'Received in House',

  rcs: 'Reference Change Senate',
  rch: 'Reference Change House',

  rs: 'Reported in the Senate',
  rh: 'Reported in the House',

  pcs: 'Placed on Calendar Senate',
  pch: 'Placed on Calendar House',

  cps: 'Considered and Passed Senate',
  cph: 'Considered and Passed House',

  eas: 'Engrossed amendment Senate',
  eah: 'Engrossed amendment House',

  es: 'Engrossed in the Senate',
  eh: 'Engrossed in the House',

  ras: 'Referred w/Amendments Senate',
  rah: 'Referred w/Amendments House',

  enr: 'Enrolled'
};

export const chamberToShort = {
  'House': 'H.R.',
  'Senate': 'S.'
}
