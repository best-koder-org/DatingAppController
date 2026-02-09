using System.Net.Http.Json;
using System.Text.Json.Serialization;
using Microsoft.EntityFrameworkCore;
using PhotoService.Data;
using PhotoService.Models;

namespace PhotoService.Services;

/// <summary>
/// Face verification service using self-hosted DeepFace container.
/// Compares selfie against profile photo using Facenet512 model.
/// </summary>
public interface IFaceVerificationService
{
    Task<VerificationResult> VerifyAsync(int userId, Stream selfieStream, string selfieFileName);
    Task<VerificationAttempt?> GetLatestAttemptAsync(int userId);
    Task<int> GetAttemptCountTodayAsync(int userId);
}

public class FaceVerificationService : IFaceVerificationService
{
    private readonly HttpClient _httpClient;
    private readonly PhotoContext _db;
    private readonly ILogger<FaceVerificationService> _logger;
    private const string DeepFaceUrl = "http://deepface:5005";
    private const int MaxAttemptsPerDay = 3;
    private const double VerifiedThreshold = 0.40;
    private const double PendingThreshold = 0.30;

    public FaceVerificationService(
        IHttpClientFactory httpClientFactory,
        PhotoContext db,
        ILogger<FaceVerificationService> logger)
    {
        _httpClient = httpClientFactory.CreateClient("DeepFace");
        _db = db;
        _logger = logger;
    }

    public async Task<VerificationResult> VerifyAsync(int userId, Stream selfieStream, string selfieFileName)
    {
        // Rate limit check
        int todayCount = await GetAttemptCountTodayAsync(userId);
        if (todayCount >= MaxAttemptsPerDay)
        {
            return new VerificationResult(
                VerificationDecision.RateLimited,
                0,
                "Maximum 3 verification attempts per day. Try again tomorrow.",
                null);
        }

        // Get user's current primary photo
        var profilePhoto = await _db.Photos
            .Where(p => p.UserId == userId && p.IsPrimary)
            .OrderByDescending(p => p.CreatedAt)
            .FirstOrDefaultAsync();

        if (profilePhoto == null)
        {
            return new VerificationResult(
                VerificationDecision.Rejected,
                0,
                "No profile photo found. Please upload a profile photo first.",
                null);
        }

        // Save selfie temporarily for DeepFace comparison
        var selfieBytes = new MemoryStream();
        await selfieStream.CopyToAsync(selfieBytes);
        var selfieBase64 = Convert.ToBase64String(selfieBytes.ToArray());

        // Call DeepFace verify endpoint
        try
        {
            var request = new DeepFaceVerifyRequest
            {
                Img1 = $"data:image/jpeg;base64,{selfieBase64}",
                Img2Path = profilePhoto.FilePath,
                ModelName = "Facenet512",
                AntiSpoofing = true
            };

            var response = await _httpClient.PostAsJsonAsync($"{DeepFaceUrl}/verify", request);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("DeepFace returned {StatusCode}", response.StatusCode);
                return new VerificationResult(
                    VerificationDecision.Error,
                    0,
                    "Verification service temporarily unavailable. Please try again later.",
                    null);
            }

            var result = await response.Content.ReadFromJsonAsync<DeepFaceVerifyResponse>();
            double similarity = 1.0 - (result?.Distance ?? 1.0); // Convert distance to similarity

            // Create attempt record
            var attempt = new VerificationAttempt
            {
                UserId = userId,
                SimilarityScore = similarity,
                ProfilePhotoId = profilePhoto.Id,
                CreatedAt = DateTime.UtcNow,
                AntiSpoofingPassed = result?.FacialArea != null
            };

            // Determine decision based on thresholds
            if (similarity >= VerifiedThreshold)
            {
                attempt.Result = "Verified";
                attempt.Decision = VerificationDecision.Verified;
            }
            else if (similarity >= PendingThreshold)
            {
                attempt.Result = "Pending";
                attempt.Decision = VerificationDecision.PendingReview;
                attempt.RejectionReason = "Borderline similarity — queued for manual review";
            }
            else
            {
                attempt.Result = "Rejected";
                attempt.Decision = VerificationDecision.Rejected;
                attempt.RejectionReason = "Face didn't match your profile photo. Please try again with better lighting.";
            }

            _db.VerificationAttempts.Add(attempt);
            await _db.SaveChangesAsync();

            return new VerificationResult(
                attempt.Decision,
                similarity,
                attempt.RejectionReason ?? "Verification successful! Your profile now has a blue badge.",
                attempt.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "DeepFace verification failed for user {UserId}", userId);
            return new VerificationResult(
                VerificationDecision.Error,
                0,
                "Verification service error. Please try again later.",
                null);
        }
    }

    public async Task<VerificationAttempt?> GetLatestAttemptAsync(int userId)
    {
        return await _db.VerificationAttempts
            .Where(a => a.UserId == userId)
            .OrderByDescending(a => a.CreatedAt)
            .FirstOrDefaultAsync();
    }

    public async Task<int> GetAttemptCountTodayAsync(int userId)
    {
        var today = DateTime.UtcNow.Date;
        return await _db.VerificationAttempts
            .CountAsync(a => a.UserId == userId && a.CreatedAt >= today);
    }
}

// DeepFace request/response models
public class DeepFaceVerifyRequest
{
    [JsonPropertyName("img1")]
    public string Img1 { get; set; } = "";

    [JsonPropertyName("img2")]
    public string Img2Path { get; set; } = "";

    [JsonPropertyName("model_name")]
    public string ModelName { get; set; } = "Facenet512";

    [JsonPropertyName("anti_spoofing")]
    public bool AntiSpoofing { get; set; } = true;
}

public class DeepFaceVerifyResponse
{
    [JsonPropertyName("verified")]
    public bool Verified { get; set; }

    [JsonPropertyName("distance")]
    public double Distance { get; set; }

    [JsonPropertyName("threshold")]
    public double Threshold { get; set; }

    [JsonPropertyName("model")]
    public string Model { get; set; } = "";

    [JsonPropertyName("facial_areas")]
    public object? FacialArea { get; set; }
}

// Verification result
public record VerificationResult(
    VerificationDecision Decision,
    double SimilarityScore,
    string Message,
    int? AttemptId
);

public enum VerificationDecision
{
    Verified,
    PendingReview,
    Rejected,
    RateLimited,
    Error
}

// EF entity for verification tracking
public class VerificationAttempt
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public double SimilarityScore { get; set; }
    public int ProfilePhotoId { get; set; }
    public string Result { get; set; } = "";
    public VerificationDecision Decision { get; set; }
    public string? RejectionReason { get; set; }
    public bool AntiSpoofingPassed { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
