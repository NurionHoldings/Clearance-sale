import {liveRuntime} from './_live/runtime.mjs';
export default async ()=>{const result=await liveRuntime().monitor();console.log(JSON.stringify({task:'studio-provider-reconciliation',...result}));};
// Published production only. Bounded work and provider timeouts keep it within 30 seconds.
export const config={schedule:'*/2 * * * *'};
