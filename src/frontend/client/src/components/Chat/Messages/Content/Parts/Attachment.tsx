import { imageExtRegex } from '~/data-provider/data-provider/src';
import type { TAttachment, TFile, TAttachmentMetadata } from '~/data-provider/data-provider/src';
import Image from '~/components/Chat/Messages/Content/Image';

export default function Attachment({ attachment }: { attachment?: TAttachment }) {
  if (!attachment) {
    return null;
  }
  const { width, height, filepath = null } = attachment as TFile & TAttachmentMetadata;
  const isImage =
    imageExtRegex.test(attachment.filename) && width != null && height != null && filepath != null;

  if (isImage) {
    return (
      <Image altText={attachment.filename} imagePath={filepath} height={height} width={width} />
    );
  }
  return null;
}
