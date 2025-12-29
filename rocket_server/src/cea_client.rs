use crate::{CEARequest, CEAResponse};

const CEA_SERVICE_URL: &str = "http://localhost:8001/cea";

pub async fn call_cea_service(request: CEARequest) -> Result<CEAResponse, reqwest::Error> {
    let client = reqwest::Client::new();
    
    let response = client
        .post(CEA_SERVICE_URL)
        .json(&request)
        .send()
        .await?
        .json::<CEAResponse>()
        .await?;
    
    Ok(response)
}
