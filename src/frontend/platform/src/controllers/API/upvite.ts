import axios from "@/controllers/request";

export async function createUpvoteApi(flow_id:string, flow_type:number, status:number) {
    return await axios.post('/api/v1/upvote', {
        flow_id,
        flow_type,
        status
    })
}

export async function updateUpvoteApi(flow_id:string, flow_type:number, status:number) {
    return await axios.put('/api/v1/upvote', {
        flow_id,
        flow_type,
        status
    })
}

export async function getUpvoteApi(flow_id:string, flow_type:number) {
    return await axios.get('/api/v1/upvote', {
        params: {
            flow_id,
            flow_type
        }
    })
}
