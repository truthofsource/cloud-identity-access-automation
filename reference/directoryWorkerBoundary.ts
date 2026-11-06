export function assertDirectoryWorkerHost(environment:Readonly<Record<string,string|undefined>>=process.env) {
  if(environment.WORKFORCE_EXECUTION_ROLE!=="directory-worker"||
    !/^func-example-directory-(nonproduction|production)-(eastus2|centralus)-001$/.test(environment.WEBSITE_SITE_NAME??""))
    throw Error("Directory writes require the dedicated Workforce directory worker.");
}

export function requireLinkedDirectoryAccount(value:string|null):string {
  if(!value||!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value))
    throw Error("An administrator must verify and link the Microsoft account before provisioning.");
  return value;
}
