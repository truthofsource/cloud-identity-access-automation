import test from "node:test";
import assert from "node:assert/strict";
import {assertDirectoryWorkerHost,requireLinkedDirectoryAccount} from "./directoryWorkerBoundary.ts";
test("directory write capability requires the dedicated host and role together",()=>{
  const allowed={WORKFORCE_EXECUTION_ROLE:"directory-worker",WEBSITE_SITE_NAME:"func-example-directory-nonproduction-eastus2-001"};
  assert.doesNotThrow(()=>assertDirectoryWorkerHost(allowed));
  for(const values of [{},{...allowed,WORKFORCE_EXECUTION_ROLE:"api"},{...allowed,WEBSITE_SITE_NAME:"func-example-workforce-nonproduction-eastus2-001"},{...allowed,WEBSITE_SITE_NAME:"localhost"}])assert.throws(()=>assertDirectoryWorkerHost(values));
});
test("directory provisioning requires an exact saved account instead of email discovery",()=>{
  assert.equal(requireLinkedDirectoryAccount("00000000-0000-4000-8000-000000000001"),"00000000-0000-4000-8000-000000000001");
  for(const value of [null,"","someone@example.invalid"])assert.throws(()=>requireLinkedDirectoryAccount(value));
});
