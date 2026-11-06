import test from "node:test";
import assert from "node:assert/strict";
import {isStaffAccessAllowed} from "./staffAccess.ts";
test("staff access preserves unbound staff but denies suspended, inactive and ambiguous bindings", () => {
  assert.equal(isStaffAccessAllowed({ suspended: false, employeeCount: 0, eligibleCount: 0 }), true);
  assert.equal(isStaffAccessAllowed({ suspended: false, employeeCount: 1, eligibleCount: 1 }), true);
  for (const state of [
    { suspended: true, employeeCount: 0, eligibleCount: 0 },
    { suspended: true, employeeCount: 1, eligibleCount: 1 },
    { suspended: false, employeeCount: 1, eligibleCount: 0 },
    { suspended: false, employeeCount: 2, eligibleCount: 2 },
  ]) assert.equal(isStaffAccessAllowed(state), false);
});
