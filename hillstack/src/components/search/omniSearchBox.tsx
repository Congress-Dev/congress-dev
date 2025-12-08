import SearchIcon from '@mui/icons-material/Search';
import Chip from '@mui/material/Chip';
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';
import type {
	ToolbarFilterOptionMap,
	ToolbarFilterSelections,
} from '~/types/components';

export interface OmniSearchBoxProps<T extends ToolbarFilterOptionMap> {
	tags: ToolbarFilterSelections<T>;
	onRemoveTag: (tag: string, value: string) => void;
	query: string;
	onQueryChange: (value: string) => void;
}

export function OmniSearchBox<T extends ToolbarFilterOptionMap>({
	tags,
	onRemoveTag,
	query,
	onQueryChange,
}: OmniSearchBoxProps<T>) {
	return (
		<TextField
			id='outlined-basic'
			onChange={(e) => onQueryChange(e.target.value)}
			placeholder='Search'
			size='small'
			slotProps={{
				input: {
					sx: { pl: 1 },
					startAdornment: (
						<InputAdornment position='start'>
							<SearchIcon />
							{Object.keys(tags).map((tag) =>
								tags[tag]?.map((subtag) => (
									<Chip
										color='primary'
										key={subtag.label}
										label={`${tag}:${subtag.label}`}
										onDelete={() => {
											onRemoveTag(
												tag,
												subtag.value as T['value'],
											);
										}}
										size='small'
										sx={{ ml: 1 }}
										variant='outlined'
									/>
								)),
							)}
						</InputAdornment>
					),
				},
			}}
			sx={{
				minWidth: '75%',
				pb: 2,
			}}
			value={query}
			variant='outlined'
		/>
	);
}
