import {getDatabase} from '@netlify/database';
import {getContext} from '@netlify/functions';
import {liveService} from './service.mjs';
import {externalProviders} from './providers.mjs';
let service;
export function liveRuntime(){
 return service??=liveService(getDatabase().pool,{gateway:externalProviders({env:name=>name==='CONTEXT'?getContext().deploy.context:Netlify.env.get(name)})});
}
