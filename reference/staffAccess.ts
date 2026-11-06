export type StaffAccessState = { suspended: boolean; employeeCount: number; eligibleCount: number };

// Unbound staff accounts remain usable: HR/Admin accounts need not be caregivers.
// A bound inactive or ambiguous identity, however, cannot use a stale role token.
export function isStaffAccessAllowed(state: StaffAccessState): boolean {
  return !state.suspended && (state.employeeCount === 0 ||
    (state.employeeCount === 1 && state.eligibleCount === 1));
}
