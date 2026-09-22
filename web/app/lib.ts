export type Reply = {type:string;text?:{body:string};template?:{name:string};interactive?:{type:string;body:{text:string};action:{buttons?:{reply:{id:string;title:string}}[];sections?:{title:string;rows:{id:string;title:string;description?:string}[]}[]}}};
export type Call={name:string;arguments:Record<string,unknown>;result:{ok:boolean;code:string;ids:string[]}};
export type Turn={id?:string;direction?:string;content_summary:string;tool_calls:Call[];created_at?:string};
export type Scenario={id:string;category:string;passed:boolean;resolution_turns:number;failures:string[];replay:Turn[];conversation_id:string;clinic_id:string};
export type Evidence={concurrency?:{requests:number;confirmed:number;rejected:number;errors:number;duration_seconds:number};dst?:{ordinary_slots:number;spring_slots:number;fall_slots:number};redteam?:{total:number;passed:number;categories:Record<string,{passed:number;total:number}>;scenarios:Scenario[]}};
export const API=process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";
export async function getJSON<T>(path:string, token:string):Promise<T>{const r=await fetch(API+path,{headers:{Authorization:"Bearer "+token}});if(!r.ok)throw new Error(r.status===401?"Enter the ops token to connect.":"The API could not complete this request.");return r.json() as Promise<T>}

