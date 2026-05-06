export default function VideoPreview({ videoUrl }) {
  return <video className="video-preview" controls src={videoUrl} autoPlay muted />;
}
