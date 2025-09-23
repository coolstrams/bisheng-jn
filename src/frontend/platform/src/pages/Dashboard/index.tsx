import { useTranslation } from "react-i18next";
import {SearchInput} from "@/components/bs-ui/input";


export default function index() {

    const { t } = useTranslation();

    return (
        <div className="px-10 py-10 h-full overflow-y-scroll scrollbar-hide relative bg-background-new border-t">
            <div className="flex gap-4">
                <SearchInput className="w-64" placeholder={t('build.searchApp')}
                             onChange={(e) => search(e.target.value)}></SearchInput>
            </div>
        </div>
    );
}