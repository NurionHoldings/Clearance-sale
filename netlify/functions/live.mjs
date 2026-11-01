import {liveRuntime} from './_live/runtime.mjs';
import {getUser} from '@netlify/identity';
import {actorFromUser} from './_ops/http.mjs';
import {liveHTTP} from './_live/http.mjs';
export default liveHTTP({service:liveRuntime,getActor:async()=>actorFromUser(await getUser())});
export const config={path:['/live-api','/live-api/*'],rateLimit:{action:'rate_limit',aggregateBy:'ip',windowSize:60,windowLimit:120}};
