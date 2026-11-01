import {getDatabase} from '@netlify/database';
import {getUser} from '@netlify/identity';
import {actorFromUser} from './_ops/http.mjs';
import {liveService} from './_live/service.mjs';
import {liveHTTP} from './_live/http.mjs';
let service;
export default liveHTTP({service:()=>service??=liveService(getDatabase().pool),getActor:async()=>actorFromUser(await getUser())});
export const config={path:['/live-api','/live-api/*'],rateLimit:{action:'rate_limit',aggregateBy:'ip',windowSize:60,windowLimit:120}};
